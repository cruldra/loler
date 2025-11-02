"""
装备数据模型
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ItemImageModel(BaseModel):
    """装备图片信息"""
    full: str = Field(..., description="完整图片文件名")
    sprite: str = Field(..., description="精灵图文件名")
    group: str = Field(..., description="图片组")
    x: int = Field(..., description="精灵图X坐标")
    y: int = Field(..., description="精灵图Y坐标")
    w: int = Field(..., description="图片宽度")
    h: int = Field(..., description="图片高度")


class ItemGoldModel(BaseModel):
    """装备金币信息"""
    base: int = Field(..., description="基础价格")
    total: int = Field(..., description="总价格")
    sell: int = Field(..., description="出售价格")
    purchasable: bool = Field(..., description="是否可购买")


class ItemStatsModel(BaseModel):
    """装备属性"""
    FlatHPPoolMod: Optional[float] = Field(default=0, description="生命值")
    FlatMPPoolMod: Optional[float] = Field(default=0, description="法力值")
    FlatArmorMod: Optional[float] = Field(default=0, description="护甲")
    FlatSpellBlockMod: Optional[float] = Field(default=0, description="魔法抗性")
    FlatPhysicalDamageMod: Optional[float] = Field(default=0, description="攻击力")
    FlatMagicDamageMod: Optional[float] = Field(default=0, description="法术强度")
    FlatMovementSpeedMod: Optional[float] = Field(default=0, description="移动速度")
    PercentAttackSpeedMod: Optional[float] = Field(default=0, description="攻击速度百分比")
    FlatCritChanceMod: Optional[float] = Field(default=0, description="暴击几率")
    PercentLifeStealMod: Optional[float] = Field(default=0, description="生命偷取")
    PercentMovementSpeedMod: Optional[float] = Field(default=0, description="移动速度百分比")


class ItemModel(BaseModel):
    """装备模型"""
    name: str = Field(..., description="装备名称")
    description: str = Field(..., description="装备描述")
    colloq: str = Field(default="", description="搜索关键词")
    plaintext: str = Field(default="", description="简单描述")
    image: ItemImageModel = Field(..., description="图片信息")
    gold: ItemGoldModel = Field(..., description="金币信息")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    maps: Dict[str, bool] = Field(default_factory=dict, description="可用地图")
    stats: ItemStatsModel = Field(default_factory=ItemStatsModel, description="属性加成")
    
    # 可选字段
    from_: Optional[List[str]] = Field(default=None, alias="from", description="合成材料")
    into: Optional[List[str]] = Field(default=None, description="可合成装备")
    depth: Optional[int] = Field(default=1, description="装备层级")
    consumed: Optional[bool] = Field(default=False, description="是否消耗品")
    inStore: Optional[bool] = Field(default=True, description="是否在商店出售")
    hideFromAll: Optional[bool] = Field(default=False, description="是否隐藏")
    requiredChampion: Optional[str] = Field(default="", description="需要的英雄")
    requiredAlly: Optional[str] = Field(default="", description="需要的队友")
    stacks: Optional[int] = Field(default=1, description="堆叠数量")
    consumeOnFull: Optional[bool] = Field(default=False, description="满层时消耗")
    specialRecipe: Optional[int] = Field(default=0, description="特殊配方")


class ItemDataModel(BaseModel):
    """装备数据集合"""
    type: str = Field(..., description="数据类型")
    version: str = Field(..., description="版本号")
    data: Dict[str, ItemModel] = Field(..., description="装备数据字典")

