from fastapi import FastAPI, Cookie, Response
import uuid
from llm import fastapi_agent

app = FastAPI()

@app.get("/chat")
def chat(
    user_input: str,
    response: Response,
    session_id: str = Cookie(default=None)
):
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True
        )

    result = fastapi_agent(user_input, session_id)

    return {
        "session_id": session_id,
        "message": result
    }
