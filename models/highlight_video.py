"""
高亮视频数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class HighlightVideo(SQLModel, table=True):
    """高亮视频表"""
    __tablename__ = "highlight_videos"

    id: Optional[int] = Field(default=None, primary_key=True, description="视频ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    name: str = Field(..., description="视频名称")
    original_path: str = Field(..., description="原始视频路径")
    converted_path: str = Field(..., description="转换后视频路径")
    file_hash: str = Field(..., index=True, description="文件哈希值")
    file_size: int = Field(..., description="文件大小(字节)")
    duration: Optional[float] = Field(default=None, description="视频时长(秒)")
    is_deleted: bool = Field(default=False, description="是否已删除")
    created_at: datetime = Field(default_factory=datetime.now, description="导入时间")
    deleted_at: Optional[datetime] = Field(default=None, description="删除时间")

