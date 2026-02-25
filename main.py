from fastapi import FastAPI, Cookie, Response, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from services.functions import convert_result
from services.llm import fastapi_agent
import psycopg
from db.connect_db import *
from enums.enum_class import messageEnum, memoryEnum
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],  # frontend của bạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str
    session_id : str

@app.post("/chat")
def chat(data: ChatRequest, request: Request, response: Response):
    # session_id = get_or_create_session(request, response)
    user_id = get_user_id(data.session_id)
    if not user_id:
        return {"error": "Cannot create user"}
    # create_conversation(user_id)
    result = fastapi_agent(data.user_input, data.session_id, int(user_id))

    return {
        "session_id": data.session_id,
        "message": convert_result(result),
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

@app.get("/conversation/{conversation_id}/messages")
def get_messages_by_conversation(conversation_id: str):
    limit = 20
    return get_messages(conversation_id, limit)

@app.get("/check_session/{session_id}")
def check_session(session_id:str):
    return check_session_id(session_id)

class UserCreate(BaseModel):
    session_id: str
    name: str | None = None
    email: str | None = None

@app.post("/create_user")
def create_user(payload: UserCreate):
    return get_user_id(
        payload.session_id,
        payload.name,
        payload.email
    )

@app.get("/create_conversation_new/{user_id}")
def create_conversation_new(user_id:int):
    return create_conversation(user_id)

@app.get("/get_latest_conversation/{user_id}")
def check_latest_conversation(user_id:int):
    return get_latest_conversation(user_id)