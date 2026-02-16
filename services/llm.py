from core.lib import *
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from services.functions import *
from services.tools import *
from services.wrap_tool_call import handle_tool_errors
from db.data_loader import vector_db
from enums.error_status import ErrorStatus, AgentResult
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path
from db.connect_db import *

load_dotenv()

DEBUG_DIR = "./agent_debug"
BASE_FILENAME = "debug"

# ================= PROMPT =================
prompt_text = read_file(Path("./prompts/system_prompt.txt"))
path_prompt_classification = Path("./prompts/prompt_classification.txt")
prompt_sumary_path = Path("./prompts/prompt_summary.txt")
prompt_clean_path = Path("./prompts/prompt_clean_question.txt")

# ================= BUSINESS PROCESS =================
bp1 = BusinessProcess("get_count_staff","lấy số lượng nhân viên",[{"get_1":get_1},{"get_2":get_2},{"get_3":get_3}])
bp2 = BusinessProcess("get_price","trích xuất giá",[{"get_4":get_4},{"get_5":get_5},{"get_6":get_6}])
bp3 = BusinessProcess("get_quanlity","kiểm tra chất lượng",[{"get_7":get_7},{"get_8":get_8},{"get_9":get_9}])
bp4 = BusinessProcess("book_meet","đặt phòng họp",[{"get_10":get_10},{"get_11":get_11},{"get_12":get_12}])
bp5 = BusinessProcess("price_ticket_movie","giá vé phim",[{"get_13":get_13},{"get_14":get_14},{"get_15":get_15}])
bp6 = BusinessProcess("get_user_by_id","lấy user theo id",[{"get_user_by_id":get_user_by_id}])

bp_list = [bp1, bp2, bp3, bp4, bp5, bp6]

prompt_template = PromptTemplate(
    template=prompt_text,
    input_variables=["knowledge", "summary"]
)

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    # model="gemini-2.0-flash",
    temperature=0,
    max_output_tokens=1024,
)

# ================= GLOBAL STORE =================
STORE = {}
SUMMARY_STORE = {}
AGENT_CACHE = {}
DEBUG_STEP = 0


# ================= HISTORY =================
def get_history(session_id: str):
    if session_id not in STORE:
        STORE[session_id] = InMemoryChatMessageHistory()
        SUMMARY_STORE[session_id] = ""

    history = STORE[session_id]

    if len(history.messages) > 10:
        conversation_text = "\n".join(
            f"{m.type}: {m.content}" for m in history.messages
        )

        SUMMARY_CHAIN = build_chain_summary(llm, prompt_sumary_path)
        summary = SUMMARY_CHAIN.invoke({
            "previous_summary": SUMMARY_STORE[session_id],
            "conversation": conversation_text
        }).content

        SUMMARY_STORE[session_id] = summary

        last_messages = history.messages[-2:]
        history.clear()
        for m in last_messages:
            history.add_message(m)

    return history


def get_or_create_agent(bp_name, tools):
    if bp_name in AGENT_CACHE:
        return AGENT_CACHE[bp_name]

    agent = create_agent(
        model=llm,
        tools=tools,
        middleware=[handle_tool_errors]
    )
    AGENT_CACHE[bp_name] = agent
    return agent


# ================= MAIN =================
def fastapi_agent(question: str, session_id: str, user_id: int) -> str:
    global DEBUG_STEP
    # user_id = get_user_id(session_id)

    payload = {
        "session_id": session_id,
        "model": {
            "model_name": llm.model,
            "temperature": llm.temperature,
            "max_tokens": llm.max_output_tokens
        },
        "steps": []
    }

    # chain_clean = build_chain_clean_question(llm, prompt_clean_path)
    # question = run_clean_question(chain_clean, user_input)

    chain_cls = build_classification_chain(llm, path_prompt_classification)
    bp_name = run_classification(chain_cls, bp_list, question).strip().lower()

    tools = []
    if bp_name == "chitchat":
        tools = [chitchat]
    elif bp_name == "knowledge_question":
        tools = [knowledge_question]
    else:
        for bp in bp_list:
            if bp.name == bp_name:
                tools = resolve_tools(bp.tools)
                break

    agent = get_or_create_agent(bp_name, tools)

    agent_with_memory = RunnableWithMessageHistory(
        agent,
        get_history,
        input_messages_key="messages",
        history_messages_key="history",
    )

    knowledge = ""
    if bp_name == "knowledge_question":
        retriever = vector_db.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(question)
        knowledge = "\n\n".join(node.text for node in nodes)

    context_summary = get_summary_by_user_id(user_id)

    result = invoke_agent_with_status(
        agent_with_memory,
        session_id,
        knowledge,
        question,
        SUMMARY_STORE,
        prompt_template,
        context_summary
    )

    history = get_history(session_id)

    conversation_id = get_conversation_id(user_id)
    import_messages(history, conversation_id)

    debug = {
        "step": DEBUG_STEP,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": question,
        "final_answer": result.answer or "",
        "status": result.status,
        "message": result.message,
        "tools": read_model(agent),
        "error_code": result.error_code,
        "trace": result.trace,
        "history": dump_history(history),
        "summary": SUMMARY_STORE.get(session_id, "")
    }

    export_debug_json(payload, debug, DEBUG_DIR, BASE_FILENAME, session_id)
    DEBUG_STEP += 1


    return result.answer or ""
