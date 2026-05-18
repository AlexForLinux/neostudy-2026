from fastapi import FastAPI
from app.routers.v1.entry import router as v1_router
from langfuse import observe, Langfuse
from app.config import settings

app = FastAPI()
app.include_router(v1_router)

langfuse = Langfuse(
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
    host=settings.langfuse_base_url
)

@app.get("/")
def hello():
    return {'message': "Hello!"}
