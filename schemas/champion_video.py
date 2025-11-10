"""
英雄教学视频数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChampionVideoCreate(BaseModel):
    """创建英雄教学视频请求"""
    champion_id: str = Field(..., description="英雄ID")
    title: str = Field(..., description="视频标题")
    url: str = Field(..., description="视频链接(B站或YouTube)")
    description: Optional[str] = Field(default=None, description="视频描述")
    platform: str = Field(default="bilibili", description="视频平台(bilibili/youtube)")


class ChampionVideoUpdate(BaseModel):
    """更新英雄教学视频请求"""
    title: Optional[str] = Field(default=None, description="视频标题")
    url: Optional[str] = Field(default=None, description="视频链接")
    description: Optional[str] = Field(default=None, description="视频描述")
    platform: Optional[str] = Field(default=None, description="视频平台")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")


class ChampionVideoResponse(BaseModel):
    """英雄教学视频响应"""
    id: int = Field(..., description="视频ID")
    user_id: int = Field(..., description="用户ID")
    champion_id: str = Field(..., description="英雄ID")
    title: str = Field(..., description="视频标题")
    url: str = Field(..., description="视频链接")
    description: Optional[str] = Field(default=None, description="视频描述")
    platform: str = Field(..., description="视频平台")
    sort_order: int = Field(..., description="排序顺序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

