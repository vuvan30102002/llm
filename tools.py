from langchain.tools import tool

@tool
def get_finance() -> str:
    """Nếu người dùng hỏi về tài chính năm 2026 thì hãy sử dụng tool này"""
    raise ValueError("Finance data source is unavailable")