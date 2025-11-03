"""
高亮视频数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HighlightVideoResponse(BaseModel):
    """高亮视频响应模型"""
    id: int = Field(..., description="视频ID")
    name: str = Field(..., description="视频名称")
    original_path: str = Field(..., description="原始视频路径")
    converted_path: str = Field(..., description="转换后视频路径")
    file_size: int = Field(..., description="文件大小(字节)")
    duration: Optional[float] = Field(default=None, description="视频时长(秒)")
    created_at: datetime = Field(..., description="导入时间")


class HighlightImportRequest(BaseModel):
    """高亮导入请求模型"""
    source_directory: str = Field(..., description="源目录路径")


class HighlightImportResponse(BaseModel):
    """高亮导入响应模型"""
    success: bool = Field(..., description="是否成功")
    imported_count: int = Field(..., description="导入数量")
    skipped_count: int = Field(..., description="跳过数量")
    message: str = Field(..., description="消息")

