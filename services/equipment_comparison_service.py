"""
装备对比AI点评服务
"""
from typing import Dict, List
import os
from crewai import Agent, Task, Crew, Process, LLM
from schemas.item import ItemModel


class EquipmentComparisonService:
    """装备对比服务"""

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

        self.analyst_agent = Agent(
            role="英雄联盟装备分析师",
            goal="分析两个装备的属性差异，提供专业的游戏建议",
            backstory="""你是一位资深的英雄联盟装备分析师，拥有多年的游戏经验。
            你擅长分析装备属性，理解不同装备在不同游戏场景下的优劣势。
            你能够根据装备的属性、价格、被动效果等因素，给出专业的建议。""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def compare_items(
        self,
        item1: ItemModel,
        item2: ItemModel,
        stats_comparison: Dict
    ) -> Dict[str, any]:
        """
        对比两个装备并生成AI点评

        Args:
            item1: 装备1
            item2: 装备2
            stats_comparison: 属性对比数据

        Returns:
            包含AI点评和标签的字典
        """
        # 构建分析任务描述
        task_description = self._build_task_description(item1, item2, stats_comparison)

        # 创建分析任务
        analysis_task = Task(
            description=task_description,
            agent=self.analyst_agent,
            expected_output="""一段150-200字的专业分析，包括：
            1. 两个装备的核心属性对比
            2. 各自的优势场景
            3. 性价比分析
            4. 推荐建议

            同时提供3-5个关键标签，如：提升生存、团战优势、性价比高、输出核心等"""
        )

        # 创建crew并执行
        crew = Crew(
            agents=[self.analyst_agent],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        # 解析结果 - result是CrewOutput对象，需要使用.raw获取文本
        return self._parse_result(result.raw)
    
    def _build_task_description(
        self,
        item1: ItemModel,
        item2: ItemModel,
        stats_comparison: Dict
    ) -> str:
        """构建任务描述"""
        description = f"""请分析以下两个英雄联盟装备的对比：

装备1: {item1.name}
- 价格: {item1.gold.total} 金币
- 简介: {item1.plaintext}
- 详细描述: {item1.description}
- 攻击力: {stats_comparison['attack_damage']['item1']}
- 法术强度: {stats_comparison['ability_power']['item1']}
- 护甲: {stats_comparison['armor']['item1']}
- 魔法抗性: {stats_comparison['magic_resist']['item1']}
- 生命值: {stats_comparison['health']['item1']}
- 暴击率: {stats_comparison['crit_chance']['item1']}%
- 攻击速度: {stats_comparison['attack_speed']['item1']}%

装备2: {item2.name}
- 价格: {item2.gold.total} 金币
- 简介: {item2.plaintext}
- 详细描述: {item2.description}
- 攻击力: {stats_comparison['attack_damage']['item2']}
- 法术强度: {stats_comparison['ability_power']['item2']}
- 护甲: {stats_comparison['armor']['item2']}
- 魔法抗性: {stats_comparison['magic_resist']['item2']}
- 生命值: {stats_comparison['health']['item2']}
- 暴击率: {stats_comparison['crit_chance']['item2']}%
- 攻击速度: {stats_comparison['attack_speed']['item2']}%

请从以下角度进行分析：
1. 属性对比：哪个装备在哪些属性上更强
2. 被动/主动效果：分析装备的特殊效果和机制
3. 适用场景：不同装备适合什么样的英雄和游戏阶段
4. 性价比：考虑价格因素，哪个装备性价比更高
5. 推荐建议：在什么情况下应该选择哪个装备

请用简洁专业的语言给出分析，并在最后用逗号分隔的方式列出3-5个关键标签。
"""
        return description
    
    def _parse_result(self, result: str) -> Dict[str, any]:
        """
        解析AI分析结果
        
        Args:
            result: AI返回的原始结果
            
        Returns:
            包含comment和tags的字典
        """
        # 尝试从结果中提取标签
        lines = result.strip().split('\n')
        
        # 假设最后一行是标签
        tags = []
        comment = result
        
        # 查找标签行（通常包含逗号分隔的关键词）
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if ',' in line and len(line) < 100:
                # 可能是标签行
                potential_tags = [tag.strip() for tag in line.split(',')]
                if len(potential_tags) >= 3 and all(len(tag) < 20 for tag in potential_tags):
                    tags = potential_tags[:5]  # 最多5个标签
                    comment = '\n'.join(lines[:i]).strip()
                    break
        
        # 如果没有找到标签，使用默认标签
        if not tags:
            tags = ["专业分析", "数据对比", "战术建议"]
        
        return {
            "comment": comment if comment else result,
            "tags": tags
        }


# 创建全局服务实例
equipment_comparison_service = EquipmentComparisonService()

