from app.schemas.chat import ChatCompletions
from app.services.service import Service
from fastapi import APIRouter, HTTPException
from litellm.exceptions import RateLimitError

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = Service.get_services().langgraph_service.run(completions)
        return response
    except RateLimitError as rle:
        raise HTTPException(402)
    except Exception as e:
        print(e)
        raise HTTPException(500, "Unexpected Error")
