from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any


class ErrorStatus(str,Enum):
    SUCCESS = "SUCCESS"                     # tac vu hoan toan thanh cong
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"     # thanh cong 1 phan, success 8 failed 2
    RETRYING = "RETRYING"                   # tac vu chua thanh cong he thong dang thu lai
    FAILED = "FAILED"                       # tac vu that bai hoan toan
    TIMEOUT = "TIMEOUT"                     # het thoi gian cho
    CANCELLED = "CANCELLED"                 # he thong bi huy, user bam cancel hoac he thong shutdown


@dataclass
class AgentResult():
    status: ErrorStatus
    message: str
    answer: Optional[str] = None
    error_code: Optional[str] = None
    trace: Optional[Any] = None