from langchain_core.messages import AIMessage, ToolMessage
from error_status import ErrorStatus, AgentResult
from error_code import ErrorCode
from langchain.messages import SystemMessage, HumanMessage
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
