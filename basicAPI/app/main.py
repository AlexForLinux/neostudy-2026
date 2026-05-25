from fastapi import FastAPI
from app.routers.v1.entry import router as v1_router
from app.config import settings

app = FastAPI()
app.include_router(v1_router)


@app.get("/")
def hello():
    return {'message': "Hello!"}
