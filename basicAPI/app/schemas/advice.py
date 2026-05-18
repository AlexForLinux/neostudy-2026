from pydantic import BaseModel, Field
from typing import List, Annotated

class Detail(BaseModel):
    title: Annotated[str, Field(
        ..., 
        description="Detail title"
    )]
    idea: Annotated[str, Field(
        ..., 
        description="Detail idea"
    )]
    
class Advice(BaseModel):
    advice_main_idea: Annotated[str, Field(
        ..., 
        description="Advice main idea"
    )]

    details: Annotated[List[Detail], Field(
        default_factory=list, 
        description="Adive details"
    )]


