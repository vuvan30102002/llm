import psycopg
from fastapi import Request, Response
import uuid
from enums.enum_class import messageEnum, memoryEnum

def connect():
    conn =  psycopg.connect(
        host = "localhost",
        port = 5432,
        dbname = "agent",
        user = "postgres",
        password = "quang123"
    )
    return conn

def create_user(session_id: str, email: str | None=None, name: str | None=None):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (session_id, email, name) VALUES (%s, %s, %s)", (session_id, email, name))
        conn.commit()
        return {
            "message" : "Successfully"
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        cur.close()
        conn.close()

def get_or_create_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=60*60*24*30,
            httponly=True,
            samesite="lax"
        )
    return session_id

def create_conversation(user_id : int, title: str | None = None, context_summary: str | None = None, is_active: bool = True):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO conversations (user_id, title, context_summary, is_active) VALUES (%s, %s, %s, %s)", (user_id, title, context_summary, is_active))
        conn.commit()
        return {
            "message": "Successfully"
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        cur.close()
        conn.close()

def create_message(conversation_id: str, role: messageEnum, content: str | None=None, tokens: int | None=None, model_name: str|None=None):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (conversation_id, role, content, tokens, model_name) VALUES (%s,%s,%s,%s,%s)", (conversation_id, role.value, content, tokens, model_name))
        conn.commit()
        return {
            "message" : "Successfully"
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        cur.close()
        conn.close()

def create_memories(user_id: int, conversation_id: str, memory_type: memoryEnum, content: str | None=None):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO memories (user_id, conversation_id, memory_type, content) VALUES (%s, %s, %s, %s)", (user_id, conversation_id, memory_type.value, content))
        conn.commit()
        return {
            "message" : "Successfully"
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        cur.close()
        conn.close()


