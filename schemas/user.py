from typing import Optional
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    provider: str = Field(..., description="OAuth提供商")
    provider_id: str = Field(..., description="提供商用户ID")
    name: str = Field(..., description="用户名")
    email: Optional[str] = Field(default="", description="邮箱")
    avatar: Optional[str] = Field(default="", description="头像URL")
    raw_data: dict = Field(default_factory=dict, description="原始数据")

