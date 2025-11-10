"""
英雄教学视频数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class ChampionVideo(SQLModel, table=True):
    """英雄教学视频表"""
    __tablename__ = "champion_videos"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="视频ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    champion_id: str = Field(..., index=True, description="英雄ID")
    title: str = Field(..., description="视频标题")
    url: str = Field(..., description="视频链接(B站或YouTube)")
    description: Optional[str] = Field(default=None, description="视频描述")
    platform: str = Field(default="bilibili", description="视频平台(bilibili/youtube)")
    sort_order: int = Field(default=0, description="排序顺序")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

