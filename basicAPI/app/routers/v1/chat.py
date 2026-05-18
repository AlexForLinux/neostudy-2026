from app.schemas.chat import ChatCompletions
from app.services.service import Service
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = Service.get_services().langgraph_service.run(completions)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(500, "Unexpected Error")
