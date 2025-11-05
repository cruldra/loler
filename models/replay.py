"""
对局录像数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Replay(SQLModel, table=True):
    """对局录像表"""
    __tablename__ = "replays"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="录像ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    name: str = Field(..., description="对局名称")
    description: Optional[str] = Field(default=None, description="描述信息")
    original_path: str = Field(..., description="导入前的文件路径")
    stored_path: str = Field(..., description="导入后的文件路径")
    file_size: int = Field(default=0, description="文件大小(字节)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

