from enum import Enum


class messageEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    AI = "ai"
    HUMAN = "human"

class memoryEnum(str, Enum):
    PROFILE = "profile"
    PREFERENCE = "preference"
    FACT = "fact"
    SUMMARY = "summary"