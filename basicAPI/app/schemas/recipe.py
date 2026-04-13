from pydantic import BaseModel, Field, conlist, confloat
from typing import List, Annotated
from annotated_types import Ge, Gt, Le, Lt
from enum import Enum

class PopularUnit(Enum):
    g = "г."
    kg = "кг."
    ml = "мл."
    l = "л."
    tsp = "ч.л."
    tbsp = "ст.л."
    pcs = "шт."
    
class Product(BaseModel):
    name: Annotated[str, Field(
        ..., 
        description="Product name in common case"
    )]
    unit: Annotated[PopularUnit | str, Field(
        ..., 
        description="Default unit of measurement for this product",
    )]

class Ingredient(BaseModel):
    product: Annotated[Product, Field(
        ..., 
        description="Product info"
    )]
    amount: Annotated[float, Gt(0), Field(
        ...,
        description="Required amount of the product"
    )]
    required: Annotated[bool, Field(
        default=True,
        description="Can the ingredient be removed or not"
    )]

class Step(BaseModel):
    title: Annotated[str, Field(
        ..., 
        description="Short title of the cooking step",
    )]
    instruction: Annotated[str, Field(
        ..., 
        description="Detailed instruction for the cooking step"
    )]
    duration: Annotated[float | None, Gt(0), Field(
        default = None,
        description = "Approximate duration of the step in minutes"
    )]
    step_utensils: Annotated[List[str], Field(
        default_factory=list,
        description="Utensils specifically needed for this step from all needed"
    )]

class Advice(BaseModel):
    title: Annotated[str, Field(
        ..., 
        description="Short title of the cooking advice",
    )]
    idea: Annotated[str, Field(
        ..., 
        description="The main idea of the advice"
    )]

class Recipe(BaseModel):
    name: Annotated[str, Field(
        ..., 
        description = "Recipe name"
    )]
    ingredients: Annotated[List[Ingredient], Field(
        default_factory=list,
        description = "Required volume of product for futher cooking"
    )]
    utensils: Annotated[List[str], Field(
        default_factory=list, 
        description="Required utensils for the futher cooking process"
    )]
    steps: Annotated[List[Step], Field(
        default_factory=list, 
        description = "Particular steps of cooking"
    )]
    advice: Annotated[List[Advice], Field(
        default_factory=list, 
        description = "Extra Advice for better cooking experience"
    )]