from pydantic import BaseModel, Field, conlist, confloat
from typing import List, Annotated
from annotated_types import Ge, Gt, Le, Lt
from enum import Enum

class Product(BaseModel):
    name: str
    unit: str

class Step(BaseModel):
    title: str
    instruction: str
    duration: float
    utensils_for_step: List[str]

class Advice(BaseModel):
    title: str
    idea: str

class Ingedient(BaseModel):
    product: Product
    amount: float
    required: bool

class LocalRecipe(BaseModel):
    name: str
    description: str
    url: str
    ingredients: List[Ingedient]
    utensils: List[str]
    steps: List[Step]
    advice: List[Advice]

    def summarize(self):
        return f"""
        Название: {self.name}
        Описание: {self.description}
        Ингредиенты: {', '.join([ingredient.product.name for ingredient in self.ingredients])}
        Утварь: {', '.join(self.utensils)}
        """.strip()



