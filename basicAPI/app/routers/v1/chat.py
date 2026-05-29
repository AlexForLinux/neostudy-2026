from app.my_schemas.chat import ChatCompletions
from app.services.service import Service
from fastapi import APIRouter, HTTPException
from openai import RateLimitError

router = APIRouter(prefix="/chat")

@router.post("/completions")
def completions(
    completions: ChatCompletions
):
    try:
        response = Service.get_services().langgraph_service.run(completions)
        return response
    except ValueError:
        raise HTTPException(400, "Invalid Input")
    except RateLimitError:
        raise HTTPException(402, "Rate Limit Exceeded")
    except Exception:
        raise HTTPException(500, "Unexpected Error")
