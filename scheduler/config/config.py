from pathlib import Path
from datetime import datetime
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "scheduler"
    LOG_DIR: Path = Path(f"log/scheduler-{datetime.now():%Y-%m-%d}.log")
    
    # 数据库配置
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings()
