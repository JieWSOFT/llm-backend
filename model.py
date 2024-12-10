from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class SysUser(SQLModel, table=True):
    id: str = Field(primary_key=True)
    username: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    lastTime: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    createTime: Optional[datetime] = Field(default=datetime.now(timezone.utc))

class TokenPayload(SQLModel):
    sub: str | None = None