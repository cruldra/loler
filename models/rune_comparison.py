"""
符文对比分析报告模型
"""
from sqlmodel import SQLModel, Field, Column, Text
from typing import Optional
from datetime import datetime


class RuneComparison(SQLModel, table=True):
    """符文对比分析报告表"""
    __tablename__ = "rune_comparisons"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="对比报告ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    
    # 对比的两个符文
    rune1_id: str = Field(..., index=True, description="符文1的ID")
    rune1_name: str = Field(..., description="符文1的名称")
    rune2_id: str = Field(..., index=True, description="符文2的ID")
    rune2_name: str = Field(..., description="符文2的名称")
    
    # AI分析结果
    ai_commentary: str = Field(..., sa_column=Column(Text), description="AI点评内容")
    ai_tags: str = Field(default="", description="AI生成的标签，逗号分隔")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

