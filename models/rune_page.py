"""
符文页数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class RunePage(SQLModel, table=True):
    """符文页表"""
    __tablename__ = "rune_pages"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="符文页ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    name: str = Field(..., description="符文页名称")
    champion_id: Optional[str] = Field(default=None, description="关联英雄ID")
    
    # 主系符文
    primary_tree_id: int = Field(..., description="主系符文树ID")
    primary_keystone_id: int = Field(..., description="主系基石符文ID")
    primary_slot1_id: int = Field(..., description="主系槽位1符文ID")
    primary_slot2_id: int = Field(..., description="主系槽位2符文ID")
    primary_slot3_id: int = Field(..., description="主系槽位3符文ID")
    
    # 副系符文
    secondary_tree_id: int = Field(..., description="副系符文树ID")
    secondary_slot1_id: int = Field(..., description="副系槽位1符文ID")
    secondary_slot2_id: int = Field(..., description="副系槽位2符文ID")
    
    # 属性碎片
    stat_shard1_id: Optional[int] = Field(default=None, description="属性碎片1ID")
    stat_shard2_id: Optional[int] = Field(default=None, description="属性碎片2ID")
    stat_shard3_id: Optional[int] = Field(default=None, description="属性碎片3ID")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

