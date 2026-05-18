from typing import Protocol

class Summarizable(Protocol):
    def summarize(self) -> str:
        ...