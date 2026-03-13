from .chat import router as chat_router
from fastapi import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(chat_router)
