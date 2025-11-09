"""
装备对比分析报告数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EquipmentComparisonCreate(BaseModel):
    """创建装备对比分析报告请求"""
    item1_id: str = Field(..., description="装备1的ID")
    item1_name: str = Field(..., description="装备1的名称")
    item2_id: str = Field(..., description="装备2的ID")
    item2_name: str = Field(..., description="装备2的名称")
    ai_commentary: str = Field(..., description="AI点评内容")
    ai_tags: str = Field(default="", description="AI生成的标签，逗号分隔")
    stats_comparison: str = Field(..., description="属性对比数据(JSON)")


class EquipmentComparisonResponse(BaseModel):
    """装备对比分析报告响应"""
    id: int = Field(..., description="对比报告ID")
    user_id: int = Field(..., description="用户ID")
    item1_id: str = Field(..., description="装备1的ID")
    item1_name: str = Field(..., description="装备1的名称")
    item2_id: str = Field(..., description="装备2的ID")
    item2_name: str = Field(..., description="装备2的名称")
    ai_commentary: str = Field(..., description="AI点评内容")
    ai_tags: str = Field(..., description="AI生成的标签，逗号分隔")
    stats_comparison: str = Field(..., description="属性对比数据(JSON)")
    created_at: datetime = Field(..., description="创建时间")

