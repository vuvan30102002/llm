from lib import *
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from functions import read_file, extract_text, messages_to_debug_json, export_debug_json
from tools import get_finance
from wrap_tool_call import handle_tool_errors

DEBUG_DIR = "./agent_debug"
BASE_FILENAME = "debug"

# ================= PROMPT =================
prompt_path = Path("./prompts/prompt_v1.txt")
prompt_text = read_file(prompt_path)
knowledge = read_file("./knowledge/financial_advice.txt")
prompt_template = PromptTemplate(
    template=prompt_text,
    input_variables=["knowledge", "question"]
)

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=[get_finance],
    middleware=[handle_tool_errors]
)

mode = "overwrite"
i = 0
session_id = "quang" + str(random.randint(100,9999))
payload = {
    "session_id" : session_id,
    "steps" : []
}

while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    system_prompt = prompt_template.format(
        knowledge=knowledge,
        question=user_input
    )

    result = agent.invoke({
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
    })

    answer = extract_text(result["messages"][-1].content)
    print(result)

    debug = {
        "step": i,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "final_answer": answer,
        "trace": messages_to_debug_json(result["messages"])
    }

    export_debug_json(payload, debug, DEBUG_DIR, BASE_FILENAME, mode=mode)
    mode = "increment"
    i += 1
