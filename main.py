from fastapi import FastAPI, Cookie, Response, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from services.llm import fastapi_agent
import psycopg
from db.connect_db import *
from enums.enum_class import messageEnum, memoryEnum

app = FastAPI()

@app.get("/chat")
def chat(user_input: str, request: Request, response: Response):
    session_id = get_or_create_session(request, response)
    user_id = get_user_id(session_id)
    if not user_id:
        return {"error": "Cannot create user"}
    # create_conversation(user_id)
    result = fastapi_agent(user_input, session_id, int(user_id))

    return {
        "session_id": session_id,
        "message": result,
        "user_id" : user_id
    }
class UserCreate(BaseModel):
    session_id : Optional[str] = Field(
        min_length=2,
        max_length=50
    )
    email: EmailStr
    name: Optional[str] = Field(
        min_length=2,
        max_length=50
    )
    
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
    session_id = get_or_create_session(request, response)
    return {
        "session_id" : session_id,
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

@app.get("/summary")
def summary(user_id: int):
    return get_summary_by_user_id(user_id)