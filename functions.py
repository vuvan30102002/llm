from langchain_core.messages import AIMessage, ToolMessage
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


def messages_to_debug_json(messages):
    data = []
    for m in messages:
        item = {
            "type": m.__class__.__name__,
            "content": extract_text(m.content)
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

def export_debug_json(data: dict, DEBUG_DIR, BASE_FILENAME, mode: str = "increment") -> str:
    os.makedirs(DEBUG_DIR, exist_ok=True)
    filepath = os.path.join(DEBUG_DIR, f"{BASE_FILENAME}.json")

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data
    }

    records = []

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                records = [records]
        except json.JSONDecodeError:
            records = []

    if mode == "overwrite":
        records = [payload]
    else:
        records.append(payload)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return filepath