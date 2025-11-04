"""
野怪数据服务类
"""
import json
from pathlib import Path
from typing import List
from schemas.monster import MonsterModel


class MonsterService:
    """野怪数据服务类"""
    
    def __init__(self):
        self.monsters: List[MonsterModel] = []
    
    def load_monsters(self, file_path: str = "data/monsters.json"):
        """
        加载野怪数据
        
        Args:
            file_path: 野怪数据文件路径
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"野怪数据文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.monsters = [MonsterModel(**monster) for monster in data]
        
        print(f"成功加载 {len(self.monsters)} 个野怪数据")
    
    def get_all_monsters(self) -> List[MonsterModel]:
        """获取所有野怪"""
        return self.monsters
    
    def get_monster_by_name(self, name: str) -> MonsterModel:
        """根据名称获取野怪"""
        for monster in self.monsters:
            if monster.name == name:
                return monster
        return None


monster_service = MonsterService()

