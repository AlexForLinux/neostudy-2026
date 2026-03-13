from pydantic import BaseModel
from typing import TypedDict, List

class Message(TypedDict):
    role: str | None
    content: str

class ChatCompletions(BaseModel):
    model: str
    messages: List[Message]
    temperature: float