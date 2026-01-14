from lib import *


# -------------------------------
# Wrapper Ollama
# -------------------------------
class OllamaLLM():
    model: str
    history: List[dict]
    client: Any

    def __init__(self, model: str, system_prompt: str = "Bạn là trợ lý AI."):
        from openai import OpenAI  # Ollama SDK
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        self.model = model
        self.history = [{"role": "system", "content": system_prompt}]

    @property
    def _llm_type(self) -> str:
        return "ollama"

    # Gọi 1 prompt
    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        self.history.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        answer = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model}


# -------------------------------
# Wrapper Google Gemini
# -------------------------------
# class GeminiLLM():
#     model: str
#     history: List[dict]
#     llm_google: Any

#     def __init__(self, model: str, system_prompt: str = "Bạn là trợ lý AI."):
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         self.model = model
#         self.llm_google = ChatGoogleGenerativeAI(model=self.model, temperature=0)
#         self.history = [{"role": "system", "content": system_prompt}]

#     @property
#     def _llm_type(self) -> str:
#         return "google_gemini"

#     def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
#         self.history.append({"role": "user", "content": prompt})
#         response = self.llm_google.invoke(prompt)
#         answer = response.content
#         self.history.append({"role": "assistant", "content": answer})
#         return answer

#     def _identifying_params(self) -> Mapping[str, Any]:
#         return {"model": self.model}


class GeminiLLM():
    model: str
    history: List[dict]
    llm_google: Any

    def __init__(self, model: str):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.model = model
        self.llm_google = ChatGoogleGenerativeAI(model=self.model, temperature=0)

    @property
    def _llm_type(self) -> str:
        return "google_gemini"

    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.llm_google.invoke(prompt)
        answer = response.content
        return answer

    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model}


# -------------------------------
# Chọn model
# -------------------------------
model_ollama = "gemma:2b"
model_gemini = "models/gemini-2.5-flash"

# Thay model ở đây
# model = "gemma:2b"  # Hoặc "models/gemini-2.5-flash"
model = "models/gemini-2.5-flash"

def model_llm(model: str):
    if model.startswith("gemma"):
        model_ollama = "gemma:2b"
        return OllamaLLM(model=model_ollama)

    elif model.startswith("models/gemini"):
        model_gemini = "models/gemini-2.5-flash"
        return GeminiLLM(model=model_gemini)

    else:
        raise ValueError(f"Model chưa được hỗ trợ: {model}")

if __name__ == "__main__":
    model = "gemma:2b"
    llm = model_llm(model)
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        answer = llm(user_input)
        print("AI:", answer)