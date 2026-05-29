from pydantic import BaseModel, Field, conlist, confloat
from typing import List

class LocalAdvice(BaseModel):
    name: str
    instruction: List[str]

    def summarize(self):
        return f"""
        Название: {self.name}
        Совет: {"; ".join(self.instruction)}
        """.strip()



