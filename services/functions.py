from langchain_core.messages import AIMessage, ToolMessage
from enums.error_status import ErrorStatus, AgentResult
from langchain.agents import create_agent
from enums.error_code import ErrorCode
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from services.tools import BusinessProcess
from services.format_output import bp_parser, clean_question, result_final
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from core.lib import *
from db.connect_db import create_message
from enums.enum_class import messageEnum

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


def messages_to_debug_json(messages):
    data = []

    for idx, m in enumerate(messages):
        item = {
            "index": idx,
            "role": m.type,   # system | human | ai | tool
            "message_type": m.__class__.__name__,
            "content": extract_text(m.content) if m.content else ""
        }
        # ✅ AI quyết định gọi tool
        if isinstance(m, AIMessage):
            if hasattr(m, "tool_calls") and m.tool_calls:
                item["tool_calls"] = []
                for call in m.tool_calls:
                    item["tool_calls"].append({
                        "tool_name": call.get("name"),
                        "tool_input": call.get("args"),
                        "tool_call_id": call.get("id")
                    })

        # ✅ Tool trả kết quả
        if isinstance(m, ToolMessage):
            item["tool_response"] = {
                "tool_name": m.name,
                "tool_call_id": m.tool_call_id,
                "output": m.content
            }

        data.append(item)

    return data


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def export_debug_json(session_payload, data: dict, DEBUG_DIR, BASE_FILENAME, session_id) -> str:
    os.makedirs(DEBUG_DIR, exist_ok=True)
    filepath = os.path.join(DEBUG_DIR, f"{BASE_FILENAME}_{session_id}.json")

    # luôn append step mới
    session_payload.setdefault("steps", []).append(data)

    records = []

    # Nếu file đã tồn tại → đọc lên
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
        except json.JSONDecodeError:
            records = []

    # Cập nhật hoặc thêm session
    updated = False
    for idx, s in enumerate(records):
        if s.get("session_id") == session_payload.get("session_id"):
            records[idx] = session_payload
            updated = True
            break

    if not updated:
        records.append(session_payload)

    # Ghi lại file
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
def dump_ai_message(msg):
    return {
        "class": msg.__class__.__name__,
        "content": msg.content,
        "additional_kwargs": msg.additional_kwargs,
        "response_metadata": msg.response_metadata,
    }

def dump_history_message(msg):
    return {
        "role" : "human" if msg.__class__.__name__ == "HumanMessage" else "AI",
        "content" : msg.content,
    }

def dump_history(history):
    return [dump_history_message(m) for m in history.messages]

# def invoke_agent_with_status(chain_with_memory, session_id, knowledge, user_input, summary_store):
#     try:
#         result = chain_with_memory.invoke(
#             {
#                 "user_input" : user_input,
#                 "knowledge" : knowledge,
#                 "summary" : summary_store.get(session_id, "")
#             },
#             config = {"configurable" : {"session_id" : session_id}}
#         )
#         return AgentResult(
#             status=ErrorStatus.SUCCESS,
#             message="Agent execution successfully",
#             answer=result.content,
#             trace=dump_ai_message(result)
#         )
#     except TimeoutError:
#         return AgentResult(
#             status=ErrorStatus.TIMEOUT,
#             message="Agent execution timeout",
#             error_code=ErrorCode.MODEL_TIMEOUT
#         )
#     except Exception as e:
#         status, msg, code = classify_gemini_error(e)

#         return AgentResult(
#             status=status,
#             message=msg,
#             error_code=code,
#             trace=str(e) 
#         )

def invoke_agent_with_status(agent_with_memory, session_id, knowledge, question, SUMMARY_STORE, prompt_template, context_summary):
    try:
        system_prompt = prompt_template.format(
            knowledge = knowledge,
            summary = SUMMARY_STORE.get(session_id, context_summary)
        )
        result = agent_with_memory.invoke(
            {
                "messages" : [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=question)
                ]
            },
            config = {"configurable" : {"session_id" : session_id}}
        )
        return AgentResult(
            status=ErrorStatus.SUCCESS,
            message="Agent execution successfully",
            answer=result["messages"][-1].content,
            trace=messages_to_debug_json([result["messages"][-1]])
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


def build_classification_chain(llm, prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables = ["business_processes", "user_input"],
        partial_variables = {
            "format_instructions" : bp_parser.get_format_instructions()
        }
    )

    chain = (prompt | llm | bp_parser)

    return chain

def run_classification(chain, bp_list, user_input):
    business_processes = "\n".join(f"- {bp.name} : {bp.description}" for bp in bp_list)
    result = chain.invoke({
        "business_processes" : business_processes,
        "user_input" : user_input
    })
    return result.business_process.strip().lower()

def build_chain_clean_question(llm, prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables = ["user_input"],
        partial_variables = {
            "format_instructions" : clean_question.get_format_instructions()
        }
    )
    chain = (prompt | llm | clean_question)
    return chain

def run_clean_question(chain, user_input):
    result = chain.invoke({
        "user_input" : user_input
    })
    return result.question

def resolve_tools(bp_tool_list):
    tools = []

    for tool_dict in bp_tool_list:
        if not isinstance(tool_dict, dict) or len(tool_dict) != 1:
            raise ValueError(f"Invalid tool definition: {tool_dict}")

        tool = next(iter(tool_dict.values()))
        tools.append(tool)

    return tools


# windown_memory = 
def build_chain_memory(llm, prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["knowledge","user_input","history","summary"],
    )
    chain = (prompt | llm )
    return chain
def build_chain_summary(llm, prompt_path):
    prompt_text = read_file(prompt_path)
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["history"]
    )
    chain = (prompt | llm)
    return chain


if __name__ == "__main__":
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0,
        max_output_tokens = 1024,
    )
    # prompt_clean_path = Path("./prompts/prompt_clean_question.txt")
    # chain = build_chain_clean_question(llm, prompt_clean_path)
    # result = run_clean_question(chain, "tài liệu nghiệp vụ thực tế")

    # print(result.question.strip().lower())