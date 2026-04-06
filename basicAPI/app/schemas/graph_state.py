from typing import TypedDict, List
from .intention import Intention
from app.schemas.chat import ChatCompletions

class MysticState(TypedDict):
    chat_story: ChatCompletions
    user_intention: Intention
    system_prompt: str
    context: List[str]
    message: str