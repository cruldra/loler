"""
英雄技巧数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class ChampionTip(SQLModel, table=True):
    """英雄技巧表"""
    __tablename__ = "champion_tips"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="技巧ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    champion_id: str = Field(..., index=True, description="英雄ID")
    title: str = Field(..., description="技巧标题")
    content: str = Field(..., description="技巧内容(Markdown格式)")
    category: str = Field(default="通用", description="技巧分类(对线/打团/出装/连招/通用)")
    sort_order: int = Field(default=0, description="排序顺序")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

