from datetime import datetime, timezone
from typing import Optional
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
    
class TokenPayload(SQLModel):
    sub: str | None = None
