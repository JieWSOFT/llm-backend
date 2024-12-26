from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class SysUser(SQLModel, table=True):
    """用户模型"""
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    openId: str = Field(default="", description="微信openId")
    username: Optional[str] = Field(default=None, max_length=255, description="用户名")
    llm_avaiable: int = Field(default=3, description="剩余使用次数")
    lastTime: datetime = Field(default_factory=datetime.now, description="最后使用时间")
    createTime: datetime = Field(default_factory=datetime.now, description="创建时间") 