from langchain.tools import tool
from dataclasses import dataclass
from typing import List
import random

@tool
def get_user_by_id(user_id: int):
    """
    Sử dụng tool này khi người dùng muốn thấy thông tin của người dùng theo id mà người dùng cung cấp
    """
    if user_id is None:
        return {
            "status" : False,
            "message" : "Người dùng chưa cung cấp thông tin mã user"
        }
    info_user = {
        111 : {
            "user_id" : user_id,
            "name" : "Vu Van Quang",
            "email" : "quang@gmail.com"
        },
        222 : {
             "user_id" : user_id,
            "name" : "Nguyen Thi Yen",
            "email" : "yen@gmail.com"
        }
    }
    return info_user.get(user_id, {"error" : "User not found"})


@dataclass
class BusinessProcess:
    name: str
    description: str
    tools: List[str]


@tool
def knowledge_question(knowledge: str, question: str) -> str:
    """
    Trả lời câu hỏi dựa trên tài liệu đã được cung cấp.
    """
    return (
        f"Dựa trên thông tin hiện có:\n{knowledge}\n\n"
        f"Vui lòng trả lời câu hỏi: {question}"
    )


@tool
def chitchat(user_input: str) -> str:
    """
    Trả lời các câu nói xã giao, chào hỏi của khách hàng.
    """
    responses = [
        "Dạ em chào anh/chị ạ 😊 Rất vui được hỗ trợ mình.",
        "Chào anh/chị, em là trợ lý của nhà hàng. Em có thể giúp gì cho mình không ạ?",
        "Dạ em xin chào ạ! Nếu anh/chị cần hỗ trợ, cứ nói em nhé."
    ]
    return random.choice(responses)



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