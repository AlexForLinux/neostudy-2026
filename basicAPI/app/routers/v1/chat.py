from app.schemas.chat import ChatCompletions
from app.services.langgraph_service import langgraph_service
from fastapi import APIRouter
import json

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = langgraph_service.run(completions)
        return response
    except:
        return {"message": "Unexpected error", "status": 500}
