"""
英雄收藏数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class ChampionFavorite(SQLModel, table=True):
    """英雄收藏表"""
    __tablename__ = "champion_favorites"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="收藏ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    champion_id: str = Field(..., index=True, description="英雄ID")
    created_at: datetime = Field(default_factory=datetime.now, description="收藏时间")

