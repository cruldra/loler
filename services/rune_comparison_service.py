"""
符文对比AI分析服务
"""
from typing import Dict, List
import os
from crewai import Agent, Task, Crew, Process, LLM
from schemas.rune import RuneModel, RuneTreeModel


class RuneComparisonService:
    """符文对比服务"""

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
            role="英雄联盟符文分析师",
            goal="分析两个符文的效果差异，提供专业的游戏建议",
            backstory="""你是一位资深的英雄联盟符文分析师，拥有多年的游戏经验。
            你擅长分析符文效果，理解不同符文在不同游戏场景下的优劣势。
            你能够根据符文的类型、效果、适用英雄等因素，给出专业的建议。""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def compare_runes(
        self,
        rune1: RuneModel,
        rune2: RuneModel,
        rune1_tree: RuneTreeModel,
        rune2_tree: RuneTreeModel,
        rune1_is_keystone: bool,
        rune2_is_keystone: bool
    ) -> Dict[str, any]:
        """
        对比两个符文并生成AI点评

        Args:
            rune1: 符文1
            rune2: 符文2
            rune1_tree: 符文1所属符文系
            rune2_tree: 符文2所属符文系
            rune1_is_keystone: 符文1是否为基石符文
            rune2_is_keystone: 符文2是否为基石符文

        Returns:
            包含AI点评和标签的字典
        """
        # 构建分析任务描述
        task_description = self._build_task_description(
            rune1, rune2, rune1_tree, rune2_tree, 
            rune1_is_keystone, rune2_is_keystone
        )

        # 创建分析任务
        analysis_task = Task(
            description=task_description,
            agent=self.analyst_agent,
            expected_output="""一段150-200字的专业分析，使用Markdown格式，包括：
            1. 两个符文的核心效果对比
            2. 各自的优势场景和适用英雄类型
            3. 符文系归属的影响
            4. 推荐建议

            同时提供3-5个关键标签，如：爆发伤害、持续输出、生存能力、机动性等"""
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
        rune1: RuneModel,
        rune2: RuneModel,
        rune1_tree: RuneTreeModel,
        rune2_tree: RuneTreeModel,
        rune1_is_keystone: bool,
        rune2_is_keystone: bool
    ) -> str:
        """构建任务描述"""
        description = f"""请分析以下两个英雄联盟符文的对比：

符文1: {rune1.name}
- 符文系: {rune1_tree.name if rune1_tree else '未知'}
- 类型: {'基石符文' if rune1_is_keystone else '普通符文'}
- 简介: {rune1.shortDesc}
- 详细描述: {rune1.longDesc}

符文2: {rune2.name}
- 符文系: {rune2_tree.name if rune2_tree else '未知'}
- 类型: {'基石符文' if rune2_is_keystone else '普通符文'}
- 简介: {rune2.shortDesc}
- 详细描述: {rune2.longDesc}

请从以下几个方面进行对比分析：
1. **核心效果对比**: 分析两个符文的核心机制和效果差异
2. **适用场景**: 什么情况下选择哪个符文更合适
3. **适用英雄**: 分别适合什么类型的英雄使用
4. **符文系影响**: 符文系归属对选择的影响
5. **优劣势分析**: 各自的优势和劣势
6. **推荐建议**: 给出专业的选择建议

请使用Markdown格式输出，包含清晰的标题和列表。
在分析的最后，用逗号分隔的方式列出3-5个关键标签。
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
            tags = ["符文对比", "专业分析", "战术建议"]
        
        return {
            "comment": comment if comment else result,
            "tags": tags
        }


# 创建全局服务实例
rune_comparison_service = RuneComparisonService()

