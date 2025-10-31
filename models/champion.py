from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ImageModel(BaseModel):
    full: str = Field(description="完整图片名称")
    sprite: str = Field(description="精灵图名称")
    group: str = Field(description="图片组")
    x: int = Field(description="X坐标")
    y: int = Field(description="Y坐标")
    w: int = Field(description="宽度")
    h: int = Field(description="高度")


class SkinModel(BaseModel):
    id: str = Field(description="皮肤ID")
    num: int = Field(description="皮肤编号")
    name: str = Field(description="皮肤名称")
    chromas: bool = Field(description="是否有炫彩")


class InfoModel(BaseModel):
    attack: int = Field(description="攻击力")
    defense: int = Field(description="防御力")
    magic: int = Field(description="魔法")
    difficulty: int = Field(description="难度")


class StatsModel(BaseModel):
    hp: float = Field(description="生命值")
    hpperlevel: float = Field(description="每级生命值")
    mp: float = Field(description="法力值")
    mpperlevel: float = Field(description="每级法力值")
    movespeed: float = Field(description="移动速度")
    armor: float = Field(description="护甲")
    armorperlevel: float = Field(description="每级护甲")
    spellblock: float = Field(description="魔抗")
    spellblockperlevel: float = Field(description="每级魔抗")
    attackrange: float = Field(description="攻击距离")
    hpregen: float = Field(description="生命回复")
    hpregenperlevel: float = Field(description="每级生命回复")
    mpregen: float = Field(description="法力回复")
    mpregenperlevel: float = Field(description="每级法力回复")
    crit: float = Field(description="暴击")
    critperlevel: float = Field(description="每级暴击")
    attackdamage: float = Field(description="攻击力")
    attackdamageperlevel: float = Field(description="每级攻击力")
    attackspeedperlevel: float = Field(description="每级攻击速度")
    attackspeed: float = Field(description="攻击速度")


class LevelTipModel(BaseModel):
    label: List[str] = Field(default_factory=list, description="标签列表")
    effect: List[str] = Field(default_factory=list, description="效果列表")


class SpellModel(BaseModel):
    id: str = Field(description="技能ID")
    name: str = Field(description="技能名称")
    description: str = Field(description="技能描述")
    tooltip: str = Field(description="技能提示")
    leveltip: Optional[LevelTipModel] = Field(default=None, description="升级提示")
    maxrank: int = Field(description="最大等级")
    cooldown: List[float] = Field(default_factory=list, description="冷却时间")
    cooldownBurn: str = Field(description="冷却时间字符串")
    cost: List[int] = Field(default_factory=list, description="消耗")
    costBurn: str = Field(description="消耗字符串")
    datavalues: Dict = Field(default_factory=dict, description="数据值")
    effect: List[Optional[List[float]]] = Field(default_factory=list, description="效果")
    effectBurn: List[Optional[str]] = Field(default_factory=list, description="效果字符串")
    vars: List = Field(default_factory=list, description="变量")
    costType: str = Field(description="消耗类型")
    maxammo: str = Field(description="最大弹药")
    range: List[int] = Field(default_factory=list, description="范围")
    rangeBurn: str = Field(description="范围字符串")
    image: ImageModel = Field(description="技能图片")
    resource: Optional[str] = Field(default=None, description="资源")


class PassiveModel(BaseModel):
    name: str = Field(description="被动名称")
    description: str = Field(description="被动描述")
    image: ImageModel = Field(description="被动图片")


class ChampionModel(BaseModel):
    id: str = Field(description="英雄ID")
    key: str = Field(description="英雄键值")
    name: str = Field(description="英雄名称")
    title: str = Field(description="英雄称号")
    image: ImageModel = Field(description="英雄图片")
    skins: List[SkinModel] = Field(default_factory=list, description="皮肤列表")
    lore: str = Field(description="英雄背景故事")
    blurb: str = Field(description="英雄简介")
    allytips: List[str] = Field(default_factory=list, description="友方提示")
    enemytips: List[str] = Field(default_factory=list, description="敌方提示")
    tags: List[str] = Field(default_factory=list, description="标签")
    partype: str = Field(description="资源类型")
    info: InfoModel = Field(description="英雄信息")
    stats: StatsModel = Field(description="英雄属性")
    spells: List[SpellModel] = Field(default_factory=list, description="技能列表")
    passive: PassiveModel = Field(description="被动技能")
    recommended: List = Field(default_factory=list, description="推荐装备")


class ChampionDataModel(BaseModel):
    type: str = Field(description="数据类型")
    format: str = Field(description="数据格式")
    version: str = Field(description="版本号")
    data: Dict[str, ChampionModel] = Field(default_factory=dict, description="英雄数据字典")

