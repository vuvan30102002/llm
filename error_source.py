from enum import Enum
class ErrorSource(str, Enum):
    USER_INPUT = "USER_INPUT"                   # du lieu nguoi dung gui len bi sai (data user send wrong)
    PREPROCESSING = "PREPROCESSING"             # loi khi lam sach, chuan hoa du lieu dau vao
    PROMPT_ENGINE = "PROMPT_ENGINE"             # prompt duoc build sai logic, thieu instruction quan trong
    MODEL = "MODEL"                             # loi say ra trong qua trinh model suy luan
    RETRIEVAL = "RETRIEVAL"                     # loi say ra khi truy xuat du lieu, khong tim duoc document, vector db down, 
    MEMORY = "MEMORY"                           # loi khi doc / ghi memory. 
    POSTPROCESSING = "POSTPROCESSING"           # loi khi format output, parse ket qua bi sai, dau ra khong dung dinh dang
    EXTERNAL_API = "EXTERNAL_API"               # loi tu ben thu 3
    INFRASTRUCTURE = "INFRASTRUCTURE"           # loi ha tang, loi he thong, server, network, cpu, ram, ..