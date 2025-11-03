"""
装备配置方案数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class ItemBuild(SQLModel, table=True):
    """装备配置方案表"""
    __tablename__ = "item_builds"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="配置方案ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    name: str = Field(..., description="配置方案名称")
    description: Optional[str] = Field(default=None, description="配置方案描述")
    champion_id: Optional[str] = Field(default=None, description="关联英雄ID")
    
    # 装备槽位 (最多6个装备)
    item_slot1: Optional[str] = Field(default=None, description="装备槽位1的装备ID")
    item_slot2: Optional[str] = Field(default=None, description="装备槽位2的装备ID")
    item_slot3: Optional[str] = Field(default=None, description="装备槽位3的装备ID")
    item_slot4: Optional[str] = Field(default=None, description="装备槽位4的装备ID")
    item_slot5: Optional[str] = Field(default=None, description="装备槽位5的装备ID")
    item_slot6: Optional[str] = Field(default=None, description="装备槽位6的装备ID")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

