"""
符文数据模型
"""
from pydantic import BaseModel, Field
from typing import List


class RuneModel(BaseModel):
    """单个符文模型"""
    id: int = Field(..., description="符文ID")
    key: str = Field(..., description="符文英文键名")
    icon: str = Field(..., description="符文图标路径")
    name: str = Field(..., description="符文中文名称")
    shortDesc: str = Field(..., description="符文简短描述")
    longDesc: str = Field(..., description="符文详细描述")


class RuneSlotModel(BaseModel):
    """符文槽位模型(每个槽位包含多个可选符文)"""
    runes: List[RuneModel] = Field(default_factory=list, description="该槽位的符文列表")


class RuneTreeModel(BaseModel):
    """符文系模型(如主宰、精密等)"""
    id: int = Field(..., description="符文系ID")
    key: str = Field(..., description="符文系英文键名")
    icon: str = Field(..., description="符文系图标路径")
    name: str = Field(..., description="符文系中文名称")
    slots: List[RuneSlotModel] = Field(default_factory=list, description="符文槽位列表")


class RunesReforgedModel(BaseModel):
    """符文重铸完整数据模型"""
    trees: List[RuneTreeModel] = Field(default_factory=list, description="所有符文系列表")

