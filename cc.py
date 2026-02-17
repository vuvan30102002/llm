from core.lib import *
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from services.functions import *
from services.tools import *
from services.wrap_tool_call import handle_tool_errors
from dotenv import load_dotenv
from db.connect_db import *

load_dotenv()

DEBUG_DIR = "./agent_debug"
BASE_FILENAME = "debug"

# ================= PROMPT =================
# prompt_text = read_file(Path("./prompts/system_prompt.txt"))
prompt_text = read_file(Path("./prompts/prompt_system.txt"))


llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    # model="gemini-2.0-flash",
    temperature=0,
    max_output_tokens=1024,
)

agent = create_agent(
    model=llm,
    system_prompt=prompt_text,
    middleware=[handle_tool_errors])


# print(dir(agent))
# print(agent.get_prompts())
# print(agent.get_graph().draw_ascii())
# print(agent._defaults)
# print(agent.config)
# print(agent.builder)
response = agent.invoke({
    "messages": [{"role": "user", "content": "bạn là ai"}]
})

print(response)

