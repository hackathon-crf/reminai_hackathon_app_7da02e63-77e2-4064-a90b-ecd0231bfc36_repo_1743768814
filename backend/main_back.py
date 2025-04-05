from fastapi import FastAPI
from backend.app.routes import router

app = FastAPI()

app.include_router(router)
