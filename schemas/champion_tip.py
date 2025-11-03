"""
英雄技巧数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChampionTipCreate(BaseModel):
    """创建英雄技巧请求"""
    champion_id: str = Field(..., description="英雄ID")
    title: str = Field(..., description="技巧标题")
    content: str = Field(..., description="技巧内容(Markdown格式)")
    category: str = Field(default="通用", description="技巧分类")


class ChampionTipUpdate(BaseModel):
    """更新英雄技巧请求"""
    title: Optional[str] = Field(default=None, description="技巧标题")
    content: Optional[str] = Field(default=None, description="技巧内容(Markdown格式)")
    category: Optional[str] = Field(default=None, description="技巧分类")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")


class ChampionTipResponse(BaseModel):
    """英雄技巧响应"""
    id: int = Field(..., description="技巧ID")
    user_id: int = Field(..., description="用户ID")
    champion_id: str = Field(..., description="英雄ID")
    title: str = Field(..., description="技巧标题")
    content: str = Field(..., description="技巧内容(Markdown格式)")
    category: str = Field(..., description="技巧分类")
    sort_order: int = Field(..., description="排序顺序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

