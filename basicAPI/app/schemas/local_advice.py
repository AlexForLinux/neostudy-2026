from pydantic import BaseModel, Field, conlist, confloat

class LocalAdvice(BaseModel):
    name: str
    instruction: str

    def summarize(self):
        return f"""
        Название: {self.name}
        Совет: {self.instruction}
        """.strip()



