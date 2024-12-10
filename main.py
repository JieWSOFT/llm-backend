import sys
from fastapi.routing import APIRoute
from api.deps import SessionDep, TokenDep, get_current_user
from core.config import settings
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from api.main import api_router
from loguru import logger
import logging

from custom_logging import InterceptHandler, format_record


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def init_app():
    # 初始化 FastAPI 应用
    app = FastAPI(
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
    logger.debug("日志系统已加载")
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    return app

app = init_app()
