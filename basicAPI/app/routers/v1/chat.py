from app.schemas.chat import ChatCompletions
from app.services.langgraph_service import langgraph_service
from fastapi import APIRouter

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
) -> dict:
    response = langgraph_service.run(completions)
    return {'message': response}

