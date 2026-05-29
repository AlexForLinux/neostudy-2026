from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class Identified(BaseModel, Generic[T]):
    id: int
    data: T

