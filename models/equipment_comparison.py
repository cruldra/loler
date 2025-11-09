"""
装备对比分析报告数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text
from datetime import datetime


class EquipmentComparison(SQLModel, table=True):
    """装备对比分析报告表"""
    __tablename__ = "equipment_comparisons"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="对比报告ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    
    # 对比的两个装备
    item1_id: str = Field(..., index=True, description="装备1的ID")
    item1_name: str = Field(..., description="装备1的名称")
    item2_id: str = Field(..., index=True, description="装备2的ID")
    item2_name: str = Field(..., description="装备2的名称")
    
    # AI分析结果
    ai_commentary: str = Field(..., sa_column=Column(Text), description="AI点评内容")
    ai_tags: str = Field(default="", description="AI生成的标签，逗号分隔")
    
    # 属性对比数据（JSON格式存储）
    stats_comparison: str = Field(..., sa_column=Column(Text), description="属性对比数据(JSON)")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

