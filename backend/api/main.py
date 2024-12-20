from fastapi import APIRouter
from api.routes.wechat_miniprogram import llm, wx
from api.routes.bms import llmTemp

api_router = APIRouter()
# 微信小程序接口
api_router.include_router(llm.router)
api_router.include_router(wx.router)

# 后端管理接口
api_router.include_router(llmTemp.router)
