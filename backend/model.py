from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import TEXT, Column
from sqlmodel import Field, SQLModel


class SysUser(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    username: str | None = Field(default=None, max_length=255)
    llm_avaiable: Optional[int] = Field(default=3)
    lastTime: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    createTime: Optional[datetime] = Field(default=datetime.now(timezone.utc))

class UserAction(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    username: str | None = Field(default=None, max_length=255)
    shareCount: Optional[int] = Field(default=None)

class UserCreateHistory(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    username: str | None = Field(default=None, max_length=255)
    content: str = Field(sa_column=Column(TEXT))
    params: str = Field(default=None)

class LLMTemplate(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    template: str = Field(sa_column=Column(TEXT))
    
class TokenPayload(SQLModel):
    sub: str | None = None
