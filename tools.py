from langchain.tools import tool
from dataclasses import dataclass
from typing import List

@tool
def get_finance(year: int) -> str:
    """
    Sử dụng tool này khi người dùng hỏi về:
    - tình hình tài chính
    - báo cáo tài chính
    - tăng trưởng tài chính

    Nếu trong câu hỏi có nhắc đến một năm cụ thể
    (ví dụ: "năm 2024", "năm 2025", "năm 2026")
    thì year chính là năm đó (kiểu số nguyên).
    """
    if year == 2026:
        return {
            "status" : "failed",
            "message": "Dữ liệu tài chính cho năm 2026 chưa được cập nhật. Bạn vui lòng đặt câu hỏi khác",
        }
    if (year == 2025):
        return {
            "status" : "success",
            "message" : f"Tài chính cho năm {year} là ổn định với mức tăng trưởng 5%."
        }
    return {
        "status" : "failed",
        "message" : "Xin lỗi, tôi không có dữ liệu tài chính cho năm bạn yêu cầu. Vui lòng thử lại với năm khác.",
    }


@dataclass
class BusinessProcess:
    name: str
    description: str
    tools: List[str]


@tool
def knowledge_question():
    """
    Dựa vào nội dung tài liệu đã được cung cấp để trả lời câu hỏi của người dùng.
    """
    return "100000"


@tool
def get_1():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_2():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_3():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_4():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_5():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_6():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_7():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_8():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_9():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_10():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_11():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_12():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_13():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_14():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_15():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_16():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_17():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_18():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"
@tool
def get_19():
    """
    Trích xuất hoặc trả về giá tiền theo yêu cầu của người dùng.
    """
    return "100000"