"""
英雄对比分析报告数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text
from datetime import datetime


class ChampionComparison(SQLModel, table=True):
    """英雄对比分析报告表"""
    __tablename__ = "champion_comparisons"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="对比报告ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    
    # 对比的两个英雄
    champion1_id: str = Field(..., index=True, description="英雄1的ID")
    champion1_name: str = Field(..., description="英雄1的名称")
    champion2_id: str = Field(..., index=True, description="英雄2的ID")
    champion2_name: str = Field(..., description="英雄2的名称")
    
    # AI分析结果
    ai_commentary: str = Field(..., sa_column=Column(Text), description="AI点评内容")
    ai_tags: str = Field(default="", description="AI生成的标签，逗号分隔")
    
    # 属性对比数据（JSON格式存储）
    stats_comparison: str = Field(..., sa_column=Column(Text), description="属性对比数据(JSON)")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

