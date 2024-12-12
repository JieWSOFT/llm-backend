import secrets
from typing import Annotated, Any
from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import time


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):

        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        print(v)
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file =  ".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    # 项目
    ENVIRONMENT: str
    PROJECT_NAME: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    LOG_DIR: str = os.path.join(os.getcwd(), f'log/{time.strftime("%Y-%m-%d")}.log')
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # LLM
    BASE_URL: str = "http://localhost:11434/v1/"
    MODEL: str = "qwen2:7b"
    API_KEY: str = 'ollama'
    # uvicorn
    SEVER_HOST: str = "0.0.0.0"
    SEVER_PORT: int = 3332

    # 路由跨域
    API_V1_STR: str = "/api/v1"
    FRONTEND_HOST: str = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # 数据库
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # 微信
    WX_APP_ID: str
    WX_APP_SECRET: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings()
