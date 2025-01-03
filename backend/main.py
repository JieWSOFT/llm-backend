from contextlib import asynccontextmanager
import http
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlmodel import Session, select
from llm.main import load_config, on_config_change, setTemplates
from model import LLMTemplate
from core.db import engine
from core.config import settings
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from api.main import api_router
from loguru import logger
import logging

from utils.custom_logging import InterceptHandler, format_record
from utils.nacos_helper import NacosHelper


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"


# 注册nacos
nacos_endpoint = settings.NACOS_ENDPOINT
nacos_namespace_id = settings.NACOS_NAMESPACE_ID
nacos_group_name = settings.NACOS_GROUPNAME
# nacos_username = 'nacos'
# nacos_password = 'nacos'
service_name = settings.PROJECT_NAME
service_port = settings.SEVER_PORT
beat_interval = settings.NACOS_BEAT_INTERVAL

nacos = NacosHelper(nacos_endpoint, nacos_namespace_id)
nacos.set_service(service_name, service_port, nacos_group_name)


# 初始化模板
@asynccontextmanager
async def lifespanself(app: FastAPI):
    # 启动前 查询模板
    with Session(engine) as session:
        templates = session.exec(select(LLMTemplate)).all()
        setTemplates(templates)
    
    # 启动 Nacos 调度器（同时设置心跳间隔）
    try:
        nacos.start_scheduler(beat_interval)
        # 尝试初始化 Nacos 服务，但不等待重试
        logger.info("Nacos服务注册开始")
        await nacos.init_service("ai_model", nacos_group_name, on_config_change)
    except Exception as e:
        logger.warning(f"Nacos服务初始化失败: {e}，应用将使用默认配置启动")
        # 不影响应用启动，后台任务会继续尝试重连
        
    yield
    
    # 结束停止的时候
    try:
        nacos.stop_scheduler()  # 这会同时处理注销服务
    except Exception as e:
        logger.error(f"Nacos服务停止异常: {e}")


def init_app():
    # 初始化 FastAPI 应用
    app = FastAPI(
        lifespan=lifespanself,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
    )

    # 添加路由
    # Set all CORS enabled origins
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)    

    # 日志
    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
    )
    logger.add(settings.LOG_DIR, encoding="utf-8", rotation="9:46")
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    return app


app = init_app()


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, e: Exception):
    logger.error(f"请求路径: {request.url}\n请求方法: {request.method}\n错误信息: {str(e)}")
    return JSONResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "message": "发生了一个内部错误，请稍后再试。",
            "details": str(e),
            "path": str(request.url),
            "method": request.method
        },
    )
