"""
召唤师技能数据服务
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from schemas.summoner import SummonerDataModel, SummonerSpellModel


class SummonerService:
    """召唤师技能数据服务类"""
    
    def __init__(self):
        self.summoner_spells: Dict[str, SummonerSpellModel] = {}
        self.version: str = ""
    
    def load_summoner_spells(self, file_path: str = "dragontail/15.21.1/data/zh_CN/summoner.json"):
        """
        加载召唤师技能数据
        
        Args:
            file_path: 召唤师技能数据文件路径
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"召唤师技能数据文件不存在: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析数据
            summoner_data = SummonerDataModel(**data)
            self.summoner_spells = summoner_data.data
            self.version = summoner_data.version
            
            print(f"成功加载 {len(self.summoner_spells)} 个召唤师技能")
            
        except Exception as e:
            print(f"加载召唤师技能数据失败: {e}")
            raise
    
    def get_all_summoner_spells(self) -> List[SummonerSpellModel]:
        """
        获取所有召唤师技能列表
        
        Returns:
            召唤师技能列表
        """
        return list(self.summoner_spells.values())
    
    def get_summoner_spell_by_id(self, spell_id: str) -> Optional[SummonerSpellModel]:
        """
        根据ID获取召唤师技能
        
        Args:
            spell_id: 召唤师技能ID
            
        Returns:
            召唤师技能对象，如果不存在则返回None
        """
        return self.summoner_spells.get(spell_id)
    
    def search_summoner_spells(self, keyword: str) -> List[SummonerSpellModel]:
        """
        搜索召唤师技能
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的召唤师技能列表
        """
        keyword = keyword.lower()
        results = []
        
        for spell in self.summoner_spells.values():
            if (keyword in spell.name.lower() or 
                keyword in spell.description.lower() or
                keyword in spell.id.lower()):
                results.append(spell)
        
        return results
    
    def get_version(self) -> str:
        """
        获取数据版本号
        
        Returns:
            版本号
        """
        return self.version


# 创建全局服务实例
summoner_service = SummonerService()

