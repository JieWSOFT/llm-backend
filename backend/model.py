from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import TEXT, Column
from sqlmodel import Field, SQLModel


class SysUser(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    openId: str = Field(default="")
    username: str | None = Field(default=None, max_length=255)
    llm_avaiable: Optional[int] = Field(default=3)
    lastTime: Optional[datetime] = Field(default_factory=datetime.now)
    createTime: Optional[datetime] = Field(default_factory=datetime.now)

class UserAction(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field()
    username: str | None = Field(default=None, max_length=255)
    shareCount: Optional[int] = Field(default=None)
    createTime: Optional[datetime] = Field(default_factory=datetime.now)


class logs(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field()
    content: str = Field(sa_column=Column(TEXT))
    createTime: Optional[datetime] = Field(default_factory=datetime.now)
    
class UserCreateHistory(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field()
    username: str | None = Field(default=None, max_length=255)
    content: str = Field(sa_column=Column(TEXT))
    params: str = Field(default=None)
    createTime: Optional[datetime] = Field(default_factory=datetime.now)


class LLMTemplate(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    template: str = (Field(sa_column=Column(TEXT)),)
    createTime: Optional[datetime] = Field(default_factory=datetime.now)

class TokenPayload(SQLModel):
    sub: str | None = None
