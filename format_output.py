from lib import *
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


class BusinessProcessOutput(BaseModel):
    business_process: str = Field(description = "Tên nghiệp vụ phù hợp nhất")

bp_parser = PydanticOutputParser(pydantic_object=BusinessProcessOutput)

class CleanQuestion(BaseModel):
    question: str = Field(description="Chuẩn hóa lại câu hỏi của người dùng để đầy đủ ý nghĩa hơn")

clean_question = PydanticOutputParser(pydantic_object=CleanQuestion)


class ResultFinal(BaseModel):
    result_final: str = Field(description="Là câu trả lời cuối cùng của agent")

result_final = PydanticOutputParser(pydantic_object=ResultFinal)