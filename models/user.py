"""
用户数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class User(SQLModel, table=True):
    """用户表"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID")
    provider: str = Field(..., description="OAuth提供商")
    provider_user_id: str = Field(..., index=True, description="提供商用户ID")
    name: str = Field(..., description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱")
    avatar: Optional[str] = Field(default=None, description="头像URL")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
