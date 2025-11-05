"""
对局录像数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReplayResponse(BaseModel):
    """录像响应模型"""
    id: int = Field(..., description="录像ID")
    name: str = Field(..., description="对局名称")
    description: Optional[str] = Field(default=None, description="描述信息")
    original_path: str = Field(..., description="导入前的文件路径")
    stored_path: str = Field(..., description="导入后的文件路径")
    file_size: int = Field(..., description="文件大小(字节)")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ReplayImportRequest(BaseModel):
    """录像导入请求模型"""
    name: str = Field(..., description="对局名称")
    description: Optional[str] = Field(default="", description="描述信息")
    original_path: str = Field(..., description="导入前的文件路径")


class ReplayImportResponse(BaseModel):
    """录像导入响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    replay_id: Optional[int] = Field(default=None, description="录像ID")


class ReplayUpdateRequest(BaseModel):
    """录像更新请求模型"""
    name: Optional[str] = Field(default=None, description="对局名称")
    description: Optional[str] = Field(default=None, description="描述信息")

