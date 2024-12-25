from contextlib import asynccontextmanager
import http
import sys
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlmodel import Session, select
from llm.main import setTemplates
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
    return f"{route.tags[0]}-{route.name}"


# 初始化模板
@asynccontextmanager
async def lifespanself(app: FastAPI):
    # 启动前 查询模板
    with Session(engine) as session:
        statement = select(LLMTemplate)
        templates = session.exec(statement).all()
        setTemplates(templates)
        logger.info(templates)
    # 注册nacos
    nacos_endpoint = "192.168.2.197:8848"
    nacos_namespace_id = ""
    nacos_group_name = "DEFAULT_GROUP"
    # nacos_username = 'nacos'
    # nacos_password = 'nacos'
    service_name = "llm-backend"
    service_port = 3332
    
    nacos = NacosHelper(nacos_endpoint, nacos_namespace_id)
    nacos.set_service(service_name, service_port, nacos_group_name)
    nacos.register()
    yield
    # 结束停止的时候


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

# 定义一个GET请求的路由，返回简单的欢迎信息及当前从Nacos获取的配置数据
@app.get("/")
def hello_world():
    return f'Hello, World! Config from Nacos: {app.state["config_data"]}'


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, e: Exception):
    logger.error(e)
    return JSONResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": str(e)},
    )
