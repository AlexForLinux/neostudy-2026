from typing import TypedDict, List
from .intention import Intention
from app.my_schemas.chat import ChatCompletions

class MysticState(TypedDict):
    chat_story: ChatCompletions
    user_intention: Intention
    context: str
    message: str