"""
野怪数据模型
"""
from pydantic import BaseModel, Field


class MonsterModel(BaseModel):
    """野怪模型"""
    name: str = Field(..., description="野怪名称")
    refreshCycle: str = Field(..., description="刷新周期(秒)")
    refreshCycleDesc: str = Field(..., description="刷新周期描述")
    firstRefreshTime: str = Field(..., description="首次刷新时间(秒)")
    firstRefreshTimeDesc: str = Field(..., description="首次刷新时间描述")
    image: str = Field(..., description="野怪图片URL")

