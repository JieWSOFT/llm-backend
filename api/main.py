from fastapi import APIRouter

from api.routes import llm,wx

api_router = APIRouter()
api_router.include_router(llm.router)
api_router.include_router(wx.router)
