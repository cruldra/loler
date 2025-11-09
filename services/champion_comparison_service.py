"""
英雄对比分析服务
"""
import os
from crewai import Agent, Task, Crew, LLM
from schemas.champion import ChampionModel


class ChampionComparisonService:
    """英雄对比分析服务"""
    
    def __init__(self):
        """初始化服务"""
        # 配置使用OpenRouter的Claude Sonnet 4.5
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # 使用crewai.LLM配置
        llm = LLM(
            model="openrouter/anthropic/claude-sonnet-4.5",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # 创建英雄分析专家Agent
        self.champion_analyst = Agent(
            role="英雄联盟英雄分析专家",
            goal="深入分析两个英雄的优劣势，提供专业的对比评价",
            backstory="""你是一位资深的英雄联盟职业分析师，拥有多年的游戏经验和深厚的理论知识。
            你擅长从多个维度分析英雄的特点，包括：
            - 基础属性和成长性
            - 技能机制和连招
            - 定位和作用
            - 对线能力
            - 团战表现
            - 适合的阵容和打法
            你的分析总是客观、专业，并且能够给出实用的建议。""",
            llm=llm,
            verbose=True
        )
    
    def compare_champions(self, champion1: ChampionModel, champion2: ChampionModel) -> str:
        """
        对比两个英雄并生成AI点评
        
        Args:
            champion1: 第一个英雄
            champion2: 第二个英雄
            
        Returns:
            AI生成的对比分析文本
        """
        # 构建对比数据
        comparison_data = self._build_comparison_data(champion1, champion2)
        
        # 创建分析任务
        task = Task(
            description=f"""请对比分析以下两个英雄联盟英雄，并提供详细的评价：

英雄1: {champion1.name} ({champion1.title})
- 定位: {', '.join(champion1.tags)}
- 资源类型: {champion1.partype}
- 基础属性:
  * 生命值: {champion1.stats.hp} (+{champion1.stats.hpperlevel}/级)
  * 法力值: {champion1.stats.mp} (+{champion1.stats.mpperlevel}/级)
  * 攻击力: {champion1.stats.attackdamage} (+{champion1.stats.attackdamageperlevel}/级)
  * 攻击速度: {champion1.stats.attackspeed} (+{champion1.stats.attackspeedperlevel}%/级)
  * 攻击距离: {champion1.stats.attackrange}
  * 护甲: {champion1.stats.armor} (+{champion1.stats.armorperlevel}/级)
  * 魔抗: {champion1.stats.spellblock} (+{champion1.stats.spellblockperlevel}/级)
  * 移速: {champion1.stats.movespeed}
- 难度: {champion1.info.difficulty}/10
- 被动技能: {champion1.passive.name} - {champion1.passive.description}
- 技能列表:
{self._format_spells(champion1.spells)}

英雄2: {champion2.name} ({champion2.title})
- 定位: {', '.join(champion2.tags)}
- 资源类型: {champion2.partype}
- 基础属性:
  * 生命值: {champion2.stats.hp} (+{champion2.stats.hpperlevel}/级)
  * 法力值: {champion2.stats.mp} (+{champion2.stats.mpperlevel}/级)
  * 攻击力: {champion2.stats.attackdamage} (+{champion2.stats.attackdamageperlevel}/级)
  * 攻击速度: {champion2.stats.attackspeed} (+{champion2.stats.attackspeedperlevel}%/级)
  * 攻击距离: {champion2.stats.attackrange}
  * 护甲: {champion2.stats.armor} (+{champion2.stats.armorperlevel}/级)
  * 魔抗: {champion2.stats.spellblock} (+{champion2.stats.spellblockperlevel}/级)
  * 移速: {champion2.stats.movespeed}
- 难度: {champion2.info.difficulty}/10
- 被动技能: {champion2.passive.name} - {champion2.passive.description}
- 技能列表:
{self._format_spells(champion2.spells)}

请从以下几个方面进行对比分析：
1. **基础属性对比**: 分析两个英雄的基础属性差异，包括生存能力、输出能力、机动性等
2. **定位和作用**: 对比两个英雄在团队中的定位和作用
3. **技能机制**: 分析技能特点和连招思路
4. **优劣势分析**: 分别说明各自的优势和劣势
5. **适用场景**: 什么情况下选择哪个英雄更合适
6. **对线建议**: 如果两个英雄对线，各自应该注意什么

请使用Markdown格式输出，包含清晰的标题和列表。""",
            expected_output="一份详细的英雄对比分析报告，使用Markdown格式，包含多个维度的对比和专业建议",
            agent=self.champion_analyst
        )
        
        # 创建Crew并执行
        crew = Crew(
            agents=[self.champion_analyst],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # 返回分析结果
        return str(result)
    
    def _build_comparison_data(self, champion1: ChampionModel, champion2: ChampionModel) -> dict:
        """构建对比数据"""
        return {
            "hp": {"champion1": champion1.stats.hp, "champion2": champion2.stats.hp},
            "hp_per_level": {"champion1": champion1.stats.hpperlevel, "champion2": champion2.stats.hpperlevel},
            "mp": {"champion1": champion1.stats.mp, "champion2": champion2.stats.mp},
            "mp_per_level": {"champion1": champion1.stats.mpperlevel, "champion2": champion2.stats.mpperlevel},
            "attack_damage": {"champion1": champion1.stats.attackdamage, "champion2": champion2.stats.attackdamage},
            "attack_damage_per_level": {"champion1": champion1.stats.attackdamageperlevel, "champion2": champion2.stats.attackdamageperlevel},
            "attack_speed": {"champion1": champion1.stats.attackspeed, "champion2": champion2.stats.attackspeed},
            "attack_speed_per_level": {"champion1": champion1.stats.attackspeedperlevel, "champion2": champion2.stats.attackspeedperlevel},
            "attack_range": {"champion1": champion1.stats.attackrange, "champion2": champion2.stats.attackrange},
            "armor": {"champion1": champion1.stats.armor, "champion2": champion2.stats.armor},
            "armor_per_level": {"champion1": champion1.stats.armorperlevel, "champion2": champion2.stats.armorperlevel},
            "magic_resist": {"champion1": champion1.stats.spellblock, "champion2": champion2.stats.spellblock},
            "magic_resist_per_level": {"champion1": champion1.stats.spellblockperlevel, "champion2": champion2.stats.spellblockperlevel},
            "move_speed": {"champion1": champion1.stats.movespeed, "champion2": champion2.stats.movespeed},
            "difficulty": {"champion1": champion1.info.difficulty, "champion2": champion2.info.difficulty}
        }
    
    def _format_spells(self, spells) -> str:
        """格式化技能列表"""
        result = []
        for i, spell in enumerate(spells, 1):
            result.append(f"  {i}. {spell.name}: {spell.description}")
        return "\n".join(result)
    
    def generate_tags(self, commentary: str) -> list:
        """
        从AI点评中提取关键标签
        
        Args:
            commentary: AI点评文本
            
        Returns:
            标签列表
        """
        # 简单的关键词提取
        keywords = []
        
        # 定位相关
        if "刺客" in commentary or "Assassin" in commentary:
            keywords.append("刺客")
        if "战士" in commentary or "Fighter" in commentary:
            keywords.append("战士")
        if "法师" in commentary or "Mage" in commentary:
            keywords.append("法师")
        if "射手" in commentary or "Marksman" in commentary:
            keywords.append("射手")
        if "坦克" in commentary or "Tank" in commentary:
            keywords.append("坦克")
        if "辅助" in commentary or "Support" in commentary:
            keywords.append("辅助")
        
        # 特点相关
        if "爆发" in commentary:
            keywords.append("爆发")
        if "持续输出" in commentary or "持续伤害" in commentary:
            keywords.append("持续输出")
        if "机动性" in commentary or "灵活" in commentary:
            keywords.append("高机动")
        if "控制" in commentary or "CC" in commentary:
            keywords.append("控制")
        if "生存" in commentary or "坦度" in commentary:
            keywords.append("高生存")
        if "团战" in commentary:
            keywords.append("团战")
        if "对线" in commentary:
            keywords.append("对线强")
        if "后期" in commentary:
            keywords.append("后期")
        if "前期" in commentary:
            keywords.append("前期")
        
        return keywords[:5]  # 最多返回5个标签


# 创建全局服务实例
champion_comparison_service = ChampionComparisonService()

