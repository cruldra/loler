"""
英雄克制关系数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class ChampionCounter(SQLModel, table=True):
    """英雄克制关系表"""
    __tablename__ = "champion_counters"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="克制关系ID")
    tier: str = Field(..., index=True, description="段位(Emerald/Diamond/Master等)")
    champion_id: str = Field(..., index=True, description="英雄ID")
    champion_name: str = Field(..., description="英雄名称")
    counter_champion_id: str = Field(..., index=True, description="被克制英雄ID")
    counter_champion_name: str = Field(..., description="被克制英雄名称")
    win_rate: float = Field(..., description="胜率")
    matches: int = Field(..., description="对局场次")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

