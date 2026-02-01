from lib import *
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from functions import *
from tools import *
from wrap_tool_call import handle_tool_errors
from data_loader import vector_db
from error_status import ErrorStatus, AgentResult
from dotenv import load_dotenv
load_dotenv()

DEBUG_DIR = "./agent_debug"
BASE_FILENAME = "debug"

# ================= PROMPT =================
prompt_text = read_file(Path("./prompts/system_prompt.txt"))
# knowledge = read_file("./knowledge/financial_advice.txt")
path_prompt_classification = Path("./prompts/prompt_classification.txt")
prompt_sumary_path = Path("./prompts/prompt_summary.txt")
prompt_clean_path = Path("./prompts/prompt_clean_question.txt")

bp1 = BusinessProcess("get_count_staff","nghiệp vụ này dùng để hướng dẫn người dùng lấy ra số lượng nhân viên",[{"get_1":get_1},{"get_2":get_2}, {"get_3":get_3}])
bp2 = BusinessProcess("get_price","nghiệp vụ này dùng để trích xuất giá tiền",[{"get_4":get_4}, {"get_5":get_5}, {"get_6":get_6}])
bp3 = BusinessProcess("get_quanlity","kiểm tra chất lượng của nhà máy",[{"get_7":get_7},{"get_8":get_8}, {"get_9":get_9}])
bp4 = BusinessProcess("book_meet","đặt lịch phòng họp",[{"get_10":get_10}, {"get_11":get_11}, {"get_12":get_12}])
bp5 = BusinessProcess("price_ticket_movie","kiểm tra giá vé xem phim",[{"get_13":get_13}, {"get_14":get_14}, {"get_15":get_15}])
bp6 = BusinessProcess("get_user_by_id","Sử dụng tool này khi người dùng muốn thấy thông tin của người dùng theo id mà người dùng cung cấp",[{"get_user_by_id":get_user_by_id}])
bp_list = [bp1, bp2, bp3, bp4, bp5, bp6]


prompt_template = PromptTemplate(
    template=prompt_text,
    input_variables=["knowledge", "summary"]
)

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0,
    max_output_tokens = 1024,
)

agent_classification = create_agent(
    model=llm,
    middleware=[handle_tool_errors]
)

mode = "overwrite"
i = 0
session_id = "quang" + str(random.randint(100,9999))
payload = {
    "session_id" : session_id,
    "model" : {
        "model_name" : llm.model,
        "temperature": llm.temperature,
        "max_tokens": llm.max_output_tokens
        },
    "steps" : []
}

store = {}
summary_store = {}

def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        summary_store[session_id] = ""

    history = store[session_id]

    if (len(history.messages) > 10):
        conversation_text = "\n".join(f"{m.type} : {m.content}" for m in history.messages)
        chain = build_chain_summary(llm, prompt_sumary_path)
        conversation = chain.invoke({
            "previous_summary": summary_store[session_id],
            "conversation" : conversation_text
        }).content
        summary_store[session_id] = conversation
        history.messages = history.messages[-2:]
    return history

def get_or_create_agent(bp_name, tools):
    if bp_name in agent_cache:
        return agent_cache[bp_name]
    agent = create_agent(
        model=llm,
        tools=tools,
        middleware=[handle_tool_errors]
    )
    agent_cache[bp_name] = agent
    return agent

while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    chain_question = build_chain_clean_question(llm, prompt_clean_path)
    question = run_clean_question(chain_question, user_input)

    chain = build_classification_chain(llm,path_prompt_classification)
    bp_llm = run_classification(chain, bp_list, question)
    
    agent_cache = {}
    select_tool = None
    for bp in bp_list:
        if bp_llm == bp.name:
            select_tool = resolve_tools(bp.tools)
            break

    if select_tool is None:
        if bp_llm == "chitchat":
            bp_name = "chitchat"
            tools = [chitchat]
        if bp_llm == "knowledge_question":
            bp_name = "knowledge_question"
            tools = [knowledge_question]
    else:
        bp_name = bp_llm
        tools = select_tool
    
    agent = get_or_create_agent(bp_name, tools)

    agent_with_memory = RunnableWithMessageHistory(
        agent,
        get_history,
        input_messages_key = "messages",
        history_messages_key = "history",
    )
    knowledge = ""
    if bp_name == "knowledge_question":
        retriever = vector_db.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(user_input)
        knowledge = "\n\n".join(node.text for node in nodes)

    result = invoke_agent_with_status(agent_with_memory, session_id, knowledge, question, summary_store, prompt_template)
    history = get_history(session_id)
    summary = summary_store.get(session_id,"")
    tools = read_model(agent)
    # tools = None    # tam thoi de do ton token
    debug = {
        "step": i,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": question,
        "final_answer": result.answer if result.answer else "",
        "status": result.status,
        "message": result.message,
        "tools": tools if tools else "",
        "error_code" : result.error_code if result.error_code else "",
        "trace": result.trace if result.trace else "",
        "history" : dump_history(history),
        "summary" : summary,
    }

    export_debug_json(payload, debug, DEBUG_DIR, BASE_FILENAME, mode=mode)
    mode = "increment"
    i += 1
