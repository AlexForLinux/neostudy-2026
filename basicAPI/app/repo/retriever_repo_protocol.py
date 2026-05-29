from typing import Protocol
from typing import TypeVar, Generic, Tuple, Generator, List
from app.my_schemas.identified import Identified

T = TypeVar('T')

class ReadableRepo(Protocol, Generic[T]):
    def get_all(self) -> Generator[Identified[T]]:
        ...
    
    def get_by_ids(self, ids: Tuple[int]) -> List[Identified[T]]:
        ...
