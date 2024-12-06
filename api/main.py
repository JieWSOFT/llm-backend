from fastapi import APIRouter

from api.routes import llm

api_router = APIRouter()
api_router.include_router(llm.router)
