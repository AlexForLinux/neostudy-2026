from app.schemas.chat import ChatCompletions
from app.services.ollama_service import ollama_service
from ollama import ResponseError
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = ollama_service.ask_llm(completions)
        response.message.content = json.loads(response.message.content) # возможно, лишнее
        return response
    
    except ResponseError as err:
        return JSONResponse(
            {"message": err.error, "status code": err.status_code}, 
            err.status_code
        )
