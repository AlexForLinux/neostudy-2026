from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    name: str
    unit: str

class ProductGroup(BaseModel):
    product: Product
    amount: float

class Recipe(BaseModel):
    name: str
    description: str
    products: List[ProductGroup]
    utensils: List[str]
    steps: List[str]