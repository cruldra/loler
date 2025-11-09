"""
英雄对比分析响应模型
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ChampionStatComparison(BaseModel):
    """单个属性对比"""
    champion1: float = Field(description="英雄1的属性值")
    champion2: float = Field(description="英雄2的属性值")


class ChampionStatsComparisonData(BaseModel):
    """英雄属性对比数据"""
    # 基础属性
    hp: ChampionStatComparison = Field(description="生命值")
    hp_per_level: ChampionStatComparison = Field(description="每级生命值")
    mp: ChampionStatComparison = Field(description="法力值")
    mp_per_level: ChampionStatComparison = Field(description="每级法力值")
    
    # 攻击属性
    attack_damage: ChampionStatComparison = Field(description="攻击力")
    attack_damage_per_level: ChampionStatComparison = Field(description="每级攻击力")
    attack_speed: ChampionStatComparison = Field(description="攻击速度")
    attack_speed_per_level: ChampionStatComparison = Field(description="每级攻击速度")
    attack_range: ChampionStatComparison = Field(description="攻击距离")
    
    # 防御属性
    armor: ChampionStatComparison = Field(description="护甲")
    armor_per_level: ChampionStatComparison = Field(description="每级护甲")
    magic_resist: ChampionStatComparison = Field(description="魔法抗性")
    magic_resist_per_level: ChampionStatComparison = Field(description="每级魔法抗性")
    
    # 移动速度
    move_speed: ChampionStatComparison = Field(description="移动速度")
    
    # 难度评级
    difficulty: ChampionStatComparison = Field(description="难度")


class ChampionComparisonResponse(BaseModel):
    """英雄对比分析响应"""
    id: int = Field(description="对比报告ID")
    user_id: int = Field(description="用户ID")
    
    champion1_id: str = Field(description="英雄1的ID")
    champion1_name: str = Field(description="英雄1的名称")
    champion2_id: str = Field(description="英雄2的ID")
    champion2_name: str = Field(description="英雄2的名称")
    
    ai_commentary: str = Field(description="AI点评内容")
    ai_tags: List[str] = Field(description="AI生成的标签列表")
    
    stats_comparison: ChampionStatsComparisonData = Field(description="属性对比数据")
    
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    version: str = Field(description="游戏版本")

