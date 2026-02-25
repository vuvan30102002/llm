import psycopg
from enums.enum_class import *
from fastapi import Request, Response
import uuid
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

def connect():
    conn =  psycopg.connect(
        # host = HOST,
        # port = PORT,
        # dbname = DBNAME,
        # user = USER,
        # password = PASSWORD
        host = "localhost",
        port = 5432,
        dbname = "agent",
        user = "postgres",
        password = "quang123"
    )
    return conn

def create_user(session_id: str, email: str | None=None, name: str | None=None):
    conn = None
    cur = None    
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
        if cur:
            cur.close()
        if conn:
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
    conn = None
    cur = None    
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO conversations (user_id, title, context_summary, is_active) VALUES (%s, %s, %s, %s)", (user_id, title, context_summary, is_active))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_message(conversation_id: str, role: messageEnum, content: str | None=None, tokens: int | None=None, model_name: str|None=None):
    conn = None
    cur = None    
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
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_memories(user_id: int, conversation_id: str, memory_type: memoryEnum, content: str | None=None):
    conn = None
    cur = None    
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
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_conversation(id: str, user_id: int, content_summary: str):
    conn = None
    cur = None    
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""UPDATE conversations SET context_summary = %s WHERE id = %s AND user_id = %s""",
            (content_summary, id, user_id)
        )
        conn.commit()
        return {
            "message" : "Successfully"
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_user_id(session_id: str, name: str|None=None, email:str|None=None):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM users WHERE session_id = %s",
            (session_id,)
        )
        row = cur.fetchone()

        if row:
            return row[0]

        # Insert nếu chưa tồn tại
        cur.execute(
            "INSERT INTO users (session_id,name,email) VALUES (%s,%s,%s) RETURNING id",
            (session_id,name,email)
        )

        user_id = cur.fetchone()[0]
        conn.commit()

        return user_id

    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_conversation_id(user_id: int):
    cur = None
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM conversations WHERE user_id = %s AND is_active = 't'",(user_id,))
        row = cur.fetchone()
        if row:
            conversation_id = row[0]
        else:
            conversation_id = None
        return conversation_id
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

ROLE_MAPPING = {
    messageEnum.USER : "user",
    messageEnum.SYSTEM : "system",
    messageEnum.ASSISTANT : "assistant",
    messageEnum.AI : "ai",
    messageEnum.HUMAN : "human",
    messageEnum.TOOL : "tool",
}

def import_messages(history_obj, conversation_id):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()

        last_two = history_obj.messages[-2:]

        for msg in last_two:

            if msg.type in ["system", "tool"] or not msg.content:
                continue

            role = ROLE_MAPPING.get(msg.type)

            if not role:
                continue

            # Kiểm tra xem tin nhắn này ĐÃ TỒN TẠI chưa trong conversation hiện tại
            cur.execute(
                "SELECT 1 FROM messages WHERE conversation_id = %s AND role = %s AND content = %s LIMIT 1",
                (conversation_id, role, msg.content)
            )
            if cur.fetchone():
                continue

            cur.execute(
                """
                INSERT INTO messages 
                (conversation_id, role, content) 
                VALUES (%s, %s, %s)
                """,
                (conversation_id, role, msg.content)
            )

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_summary_by_user_id(user_id: int):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT context_summary FROM conversations WHERE user_id = %s AND is_active = 't'",(user_id,))
        row = cur.fetchone()
        if row:
            summary = row[0]
        else:
            summary = None
        return summary
    except Exception as e:
        return{
            "error" : str(e)
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_conversation(user_id: int, context_summary: str):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE conversations
            SET context_summary = %s
            WHERE user_id = %s AND is_active = 't'
            """,
            (context_summary, user_id)
        )
        conn.commit()   
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_messages(conversation_id: str, limit: int):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC LIMIT %s", (conversation_id, limit))
        rows = cur.fetchall()
        if rows:
            messages = [
                {
                    "role" : r[0],
                    "content" : r[1],
                }
                for r in rows
            ]
        return {
            "messages" : messages
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def check_session_id(session_id: str):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE session_id = %s",(session_id,))
        row = cur.fetchone()
        if row:
            return row[0]
        else:
            return None 
    except Exception as e:
        return None
    
def get_latest_conversation(user_id: int):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM conversations WHERE user_id = %s",(user_id,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except Exception as e:
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
