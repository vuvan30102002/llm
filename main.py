from fastapi import FastAPI, Cookie, Response, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
# from llm import fastapi_agent
import psycopg
from db.connect_db import *
from enums.enum_class import messageEnum, memoryEnum

app = FastAPI()

# @app.get("/chat")
# def chat(
#     user_input: str,
#     response: Response,
#     session_id: str = Cookie(default=None)
# ):
#     if not session_id:
#         session_id = str(uuid.uuid4())
#         response.set_cookie(
#             key="session_id",
#             value=session_id,
#             httponly=True
#         )

#     result = fastapi_agent(user_input, session_id)

#     return {
#         "session_id": session_id,
#         "message": result
#     }
class UserCreate(BaseModel):
    session_id : Optional[str]
    email: EmailStr
    name: Optional[str]
    
class Conversation(BaseModel):
    user_id : int
    title: Optional[str] = Field(
        default=None,
        examples=[""]
    )
    context_summary: Optional[str] = Field(
        default=None,
        examples=[""]
    )
    is_active: bool = True

class Message(BaseModel):
    conversation_id: str
    role: messageEnum
    content : Optional[str] = Field(
        default=None,
        examples=[""]
    )
    tokens: Optional[int]
    model_name: Optional[str] = Field(
        default=None,
        examples=[""]
    )

class Memory(BaseModel):
    user_id: int
    conversation_id : str
    memory_type : memoryEnum
    content: Optional[str] = Field(
        default=None,
        examples=[""]
    )


@app.post("/start-chat")
def start_chat(payload: UserCreate):
    return create_user(payload.session_id, payload.email, payload.name)

@app.get("/get-session")
def get_session(request: Request, response: Response):
    session = get_or_create_session(request, response)
    return {
        "session_id" : session,
    }

@app.post("/conversation")
def conversation(payload: Conversation):
    return create_conversation(payload.user_id, payload.title, payload.context_summary, payload.is_active)

@app.post("/message")
def message(payload: Message):
    return create_message(payload.conversation_id, payload.role, payload.content, payload.tokens, payload.model_name)

@app.post("/memory")
def memory(payload: Memory):
    return create_memories(payload.user_id, payload.conversation_id, payload.memory_type, payload.content)