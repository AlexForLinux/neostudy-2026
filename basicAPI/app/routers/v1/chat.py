from app.schemas.chat import ChatCompletions
from app.services.service import Service
from fastapi import APIRouter

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = Service.get_services().langgraph_service.run(completions)
        return response
    except Exception as e:
        return {"status": 500, "message": e}
