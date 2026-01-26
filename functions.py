from langchain_core.messages import AIMessage, ToolMessage
from error_status import ErrorStatus, AgentResult
from langchain.agents import create_agent
from error_code import ErrorCode
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from tools import BusinessProcess
from lib import *

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return str(content)


def messages_to_debug_json(messages, prompt_template):
    data = []
    for m in messages:
        item = {
            "type": m.__class__.__name__,
            "content": extract_text(m.content)
        }
        if isinstance(m, SystemMessage):
            item["quang"] = {
                "prompt_text" : prompt_template.template,
                "input_variables" : prompt_template.input_variables
            }
        if isinstance(m, AIMessage) and m.tool_calls:
            item["tool_calls"] = m.tool_calls
        if isinstance(m, ToolMessage):
            item["tool_call_id"] = m.tool_call_id
        data.append(item)
    return data


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def export_debug_json(session_payload, data: dict, DEBUG_DIR, BASE_FILENAME, mode: str = "increment") -> str:
    os.makedirs(DEBUG_DIR, exist_ok=True)
    filepath = os.path.join(DEBUG_DIR, f"{BASE_FILENAME}.json")

    session_payload["steps"].append(data)     

    if mode == "overwrite" or not os.path.exists(filepath):
        records = [session_payload]
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            for idx, s in enumerate(records):
                if s["session_id"] == session_payload["session_id"]:
                    records[idx] = session_payload
                    break
                else:
                    records.append(session_payload)
        except json.JSONDecodeError:
            pass

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        
    return filepath

def classify_gemini_error(err: Exception):
    msg = str(err).lower()

    if "quota" in msg or "resource_exhausted" in msg:
        return ErrorStatus.FAILED, "Gemini quota exceeded", ErrorCode.MODEL_QUOTA_EXCEEDED

    if "api key" in msg or "permission" in msg:
        return ErrorStatus.FAILED, "Invalid Gemini API key", ErrorCode.MODEL_INVALID_API_KEY

    if "token" in msg or "max_output_tokens" in msg:
        return ErrorStatus.FAILED, "Max output tokens exceeded", ErrorCode.MODEL_MAX_TOKEN_EXCEEDED

    if "timeout" in msg or "deadline" in msg:
        return ErrorStatus.TIMEOUT, "Gemini request timeout", ErrorCode.MODEL_TIMEOUT

    return ErrorStatus.FAILED, "Unknown Gemini error", ErrorCode.MODEL_UNRESPONSE


def invoke_agent_with_status(agent, system_prompt, user_input, prompt_template):
    try:
        result = agent.invoke({
            "messages" : [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
        })
        answer = extract_text(result["messages"][-1].content)
        trace=messages_to_debug_json(result["messages"], prompt_template)
        return AgentResult(
            status=ErrorStatus.SUCCESS,
            message="Agent execution successfully",
            answer= answer,
            trace=trace
        )
    except TimeoutError:
        return AgentResult(
            status=ErrorStatus.TIMEOUT,
            message="Agent execution timeout",
            error_code=ErrorCode.MODEL_TIMEOUT
        )
    except Exception as e:
        status, msg, code = classify_gemini_error(e)

        return AgentResult(
            status=status,
            message=msg,
            error_code=code,
            trace=str(e) 
        )
    
def read_model(agent):
    graph = agent.get_graph()
    tool_node = graph.nodes.get("tools")
    if tool_node is None:
        return []
    
    tools = []
    for tool in tool_node.data._tools_by_name.values():
        tools.append({
            "name": tool.name,
            "description": tool.description,
        })
    return tools

def read_prompt_classification(path: Path, bp_list: List[BusinessProcess], user_input: str):
    with open(path, "r", encoding="utf-8") as f:
        description = f.read()

    # Convert dict -> text
    business_processes = "\n".join(
        f"- {bp.name}: {bp.description}" for bp in bp_list
    )

    prompt_template = PromptTemplate(
        template=description,
        input_variables=["business_processes","user_input"]
    )

    prompt = prompt_template.format(
        business_processes=business_processes,
        user_input = user_input
    )

    return prompt

# bp1 = BusinessProcess("get_count_staff","nghiệp vụ này dùng để hướng dẫn người dùng lấy ra số lượng nhân viên",["get_1","get_2","get_3"])
# bp2 = BusinessProcess("get_price","nghiệp vụ này dùng để trích xuất giá tiền",["get_4","get_5","get_6"])
# bp3 = BusinessProcess("get_quanlity","kiểm tra chất lượng của nhà máy",["get_9","get_8","get_7"])
# bp4 = BusinessProcess("book_meet","đặt lịch phòng họp",["get_12","get_11","get_10"])
# bp5 = BusinessProcess("price_ticket_movie","kiểm tra giá vé xem phim",["get_13","get_14","get_15"])

# path = Path("./prompts/prompt_classification.txt")
# bp_list = [bp1, bp2, bp3, bp4, bp5]
# a = read_prompt_classification(path, bp_list, user_input="hom nay co mua hay khong")
# print(a)


def invoke_agent_classification(agent, prompt_classification, user_input):
    try:
        response = agent.invoke({
            "messages" : [
                SystemMessage(content=prompt_classification),
                HumanMessage(content=user_input)
            ]
        })
        result = response["messages"][-1].content
        return result

    except Exception as e:
        return "khong goi duoc agent"


def extract_first_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON object found")

    data = json.loads(text[start:end])
    intent = data.get("business_process")

    return intent

def extract_bp(agent, prompt_classification, bp_list, user_input)->str:
    prompt = read_prompt_classification(prompt_classification, bp_list, user_input)
    result = invoke_agent_classification(agent, prompt, user_input)
    bp = extract_first_json(result)
    return bp.strip().lower()

def resolve_tools(bp_tool_list):
    tools = []

    for tool_dict in bp_tool_list:
        if not isinstance(tool_dict, dict) or len(tool_dict) != 1:
            raise ValueError(f"Invalid tool definition: {tool_dict}")

        tool = next(iter(tool_dict.values()))
        tools.append(tool)

    return tools

