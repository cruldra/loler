"""
召唤师技能数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class SummonerImageModel(BaseModel):
    """召唤师技能图片模型"""
    full: str = Field(..., description="完整图片名称")
    sprite: str = Field(..., description="精灵图名称")
    group: str = Field(..., description="图片组")
    x: int = Field(..., description="X坐标")
    y: int = Field(..., description="Y坐标")
    w: int = Field(..., description="宽度")
    h: int = Field(..., description="高度")


class SummonerSpellModel(BaseModel):
    """召唤师技能模型"""
    id: str = Field(..., description="技能ID")
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能描述")
    tooltip: str = Field(..., description="技能提示")
    maxrank: int = Field(..., description="最大等级")
    cooldown: List[float] = Field(default_factory=list, description="冷却时间")
    cooldownBurn: str = Field(..., description="冷却时间字符串")
    cost: List[int] = Field(default_factory=list, description="消耗")
    costBurn: str = Field(..., description="消耗字符串")
    datavalues: Dict = Field(default_factory=dict, description="数据值")
    effect: List[Optional[List[float]]] = Field(default_factory=list, description="效果")
    effectBurn: List[Optional[str]] = Field(default_factory=list, description="效果字符串")
    vars: List = Field(default_factory=list, description="变量")
    key: str = Field(..., description="技能键值")
    summonerLevel: int = Field(..., description="召唤师等级要求")
    modes: List[str] = Field(default_factory=list, description="可用模式")
    costType: str = Field(..., description="消耗类型")
    maxammo: str = Field(..., description="最大弹药")
    range: List[int] = Field(default_factory=list, description="范围")
    rangeBurn: str = Field(..., description="范围字符串")
    image: SummonerImageModel = Field(..., description="技能图片")
    resource: str = Field(..., description="资源")


class SummonerDataModel(BaseModel):
    """召唤师技能数据模型"""
    type: str = Field(..., description="数据类型")
    version: str = Field(..., description="版本号")
    data: Dict[str, SummonerSpellModel] = Field(default_factory=dict, description="召唤师技能数据")

