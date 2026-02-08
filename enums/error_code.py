from enum import Enum
class ErrorCode(str, Enum):
    # USER
    INVALID_USER_INPUT = "INVALID_USER_INPUT"                      # input nguoi dung khong hop le, json sai format, thieu field bat buoc, gia tri khong dung kieu
    # PROMPT
    PROMPT_TEMPLATE_ERROR = "PROMPT_TEMPLATE_ERROR"                # loi trong template prompt, sai cu phap, template loi logic
    PROMPT_VARIABLE_MISSING = "PROMPT_VARIABLE_MISSING"            # prompt can bien nhung khong truyen vao
    # MODEL
    MODEL_TIMEOUT = "MODEL_TIMEOUT"                                # model xu ly qua thoi gian cho phep
    MODEL_RATE_LIMITED = "MODEL_RATE_LIMITED"                      # model bi gioi han request
    MODEL_EMPTY_RESPONSE = "MODEL_EMPTY_RESPONSE"                  # model tra ve rong khong co content
    MODEL_OUTPUT_PARSE_FAILED = "MODEL_OUTPUT_PARSE_FAILED"        # model duoc yeu cau tra ve json nhung lai tra ra text thuong
    # RETRIEVAL
    VECTOR_INDEX_NOT_FOUND = "VECTOR_INDEX_NOT_FOUND"              # vector db khong co index
    VECTOR_EMPTY_RESULT = "VECTOR_EMPTY_RESULT"                    # khong tim duoc tai lieu lien quan
    # MEMORY
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"                        # khong tim thay session
    SESSION_EXPIRED = "SESSION_EXPIRED"                            # session da het han
    # INFRA
    DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED"                  # khong ket noi duoc db
    CACHE_UNAVAILABLE = "CACHE_UNAVAILABLE"                        # cache bi down
    # Model is unreponse
    MODEL_UNRESPONSE = "MODEL_UNRESPONSE"

    MODEL_QUOTA_EXCEEDED = "MODEL_QUOTA_EXCEEDED"
    MODEL_INVALID_API_KEY = "MODEL_INVALID_API_KEY"
    MODEL_MAX_TOKEN_EXCEEDED = "MODEL_MAX_TOKEN_EXCEEDED"