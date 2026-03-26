from typing import TypedDict
from .intention import Intention
from app.schemas.chat import ChatCompletions

class MysticState(TypedDict):
    user_query: ChatCompletions
    user_intention: Intention
    message: str