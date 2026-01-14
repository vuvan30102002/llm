from abstraction_llm import model_llm, OllamaLLM, GeminiLLM
from lib import *


def read_file_prompt(path: str)->str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

question = "sơn tùng có phải là ca sỹ không"

prompt_path = Path("./prompts/prompt_v1.txt")
knowledge_path = "./knowledge/financial_advice.txt"

def ask_llm(question:str)->str:
    prompt_text = read_file_prompt(prompt_path)
    knowledge = read_file_prompt(knowledge_path)

    prompt = PromptTemplate(
        template = prompt_text,
        input_variables=["knowledge","question"]
    )

    final_prompt = prompt.format(knowledge=knowledge, question=question)
    llm = model_llm("models/gemini-2.5-flash")
    answer = llm(final_prompt)
    return answer

print(ask_llm(question))