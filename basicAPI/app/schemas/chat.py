from pydantic import BaseModel, Field
from typing import TypedDict, List, Literal, Annotated

class Message(TypedDict):
    role: Annotated[str | None, Field(default='user', description='role')]
    content: Annotated[str, Field(..., description='user request')]

class ChatCompletions(BaseModel):
    model: Annotated[
        Literal["gpt-oss-120b", "qwen-3-235b-a22b-instruct-2507"],
        Field(default='gpt-oss-120b', description='model')
    ]
    messages: Annotated[List[Message], Field(default_factory=list, description='chat messages')]
    temperature: Annotated[float, Field(default=0, description='temperature')]