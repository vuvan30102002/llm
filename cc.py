from LLM.core.lib import *
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from LLM.services.functions import *
from LLM.services.tools import *
from LLM.services.wrap_tool_call import handle_tool_errors
from LLM.enums.error_status import ErrorStatus, AgentResult


DEBUG_DIR = "./agent_debug"
BASE_FILENAME = "debug"

# ================= PROMPT =================
knowledge = read_file("./knowledge/financial_advice.txt")
path_prompt_classification = Path("./prompts/prompt_classification.txt")
prompt_clean_path = Path("./prompts/prompt_clean_question.txt")


prompt_system_test = read_file(Path("./prompts/prompt_system_test.txt"))


bp1 = BusinessProcess("get_count_staff","nghiệp vụ này dùng để hướng dẫn người dùng lấy ra số lượng nhân viên",[{"get_1":get_1},{"get_2":get_2}, {"get_3":get_3}])
bp2 = BusinessProcess("get_price","nghiệp vụ này dùng để trích xuất giá tiền",[{"get_4":get_4}, {"get_5":get_5}, {"get_6":get_6}])
bp3 = BusinessProcess("get_quanlity","kiểm tra chất lượng của nhà máy",[{"get_7":get_7},{"get_8":get_8}, {"get_9":get_9}])
bp4 = BusinessProcess("book_meet","đặt lịch phòng họp",[{"get_10":get_10}, {"get_11":get_11}, {"get_12":get_12}])
bp5 = BusinessProcess("price_ticket_movie","kiểm tra giá vé xem phim",[{"get_13":get_13}, {"get_14":get_14}, {"get_15":get_15}])
bp6 = BusinessProcess("get_user_by_id","Sử dụng tool này khi người dùng muốn thấy thông tin của người dùng theo id mà người dùng cung cấp",[{"get_user_by_id":get_user_by_id}])
bp_list = [bp1, bp2, bp3, bp4, bp5, bp6]


prompt_template = PromptTemplate(
    template=prompt_system_test,
    input_variables=["knowledge", "question"]
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

def invoke_agent_with_test(agent, question , systemprompt, prompt_template):
    try:
        result = agent.invoke(
            {
            "messages" : [
                    SystemMessage(content=systemprompt),
                    HumanMessage(content=question.question)
                ]
            },
            return_intermediate_steps=True,
        )
        answer = extract_text(result["messages"][-1].content)
        trace=messages_to_debug_json(result["messages"], prompt_template)
        return AgentResult(
            status=ErrorStatus.SUCCESS,
            message="Agent execution successfully",
            answer=answer,
            trace=trace
        )
    except Exception as e:
        status, msg, code = classify_gemini_error(e)
        return AgentResult(
            status=status,
            message=msg,
            error_code=code,
            trace=str(e) 
        )


while True:
    user_input = input("You: ")
    if user_input == "exit":
        break
    chain_question = build_chain_clean_question(llm, prompt_clean_path)
    question = run_clean_question(chain_question, user_input)

    chain_classification = build_classification_chain(llm,path_prompt_classification)
    bp_llm = run_classification(chain_classification, bp_list, question)
    # print(bp_llm)
    select_tool = None
    for bp in bp_list:
        if bp_llm == bp.name:
            select_tool = resolve_tools(bp.tools)
            break
    if select_tool is None:
        agent = create_agent(
            model=llm,
            tools = [knowledge_question],
            middleware=[handle_tool_errors]
        )
    else:
        agent = create_agent(
            model=llm,
            tools=select_tool,
            middleware=[handle_tool_errors]
        )


    systemprompt = prompt_template.format(knowledge=knowledge, question=question)

    result = invoke_agent_with_test(agent, question, systemprompt, prompt_template)
    tools = read_model(agent)
    debug = {
        "step": i,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": question.question,
        "final_answer": result.answer if result.answer else "",
        "status": result.status,
        "message": result.message,
        "tools": tools if tools else "",
        "error_code" : result.error_code if result.error_code else "",
        "trace": result.trace if result.trace else "",
    }

    export_debug_json(payload, debug, DEBUG_DIR, BASE_FILENAME, mode=mode)
    mode = "increment"
    i += 1
