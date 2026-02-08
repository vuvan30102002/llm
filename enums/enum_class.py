from enum import Enum


class messageEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class memoryEnum(str, Enum):
    PROFILE = "profile"
    PREFERENCE = "preference"
    FACT = "fact"
    SUMMARY = "summary"