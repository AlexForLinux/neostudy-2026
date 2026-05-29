from pydantic import BaseModel, Field
from typing import Annotated

#Pydantic схемы для описания моделей инструментов

#Модель инструмента на базе текстового ретривера
class GetRecipesTool(BaseModel):
    query: Annotated[str, Field(
        ..., 
        description="User query"
    )]

#Модель инструмента поиска ресурсов в Интернете
class WebSearchTool(BaseModel):
    query: Annotated[str, Field(
        ..., 
        description="Browsing query for Internet Search"
    )]

#Модель чтения веб-страниц
class UrlReaderTool(BaseModel):
    url: Annotated[str, Field(
        ..., 
        description="Url of a web-page"
    )]

class FinishTool(BaseModel):
    pass #фиктивный инструмент для обозначения завершения работы