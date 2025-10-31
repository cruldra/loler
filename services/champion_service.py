import json
from pathlib import Path
from typing import Dict, Optional
from models.champion import ChampionDataModel, ChampionModel


class ChampionService:
    def __init__(self):
        self._champion_data: Optional[ChampionDataModel] = None
        self._champions: Dict[str, ChampionModel] = {}
    
    def load_champions(self, file_path: str = "dragontail/15.21.1/data/zh_CN/championFull.json"):
        json_path = Path(file_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"英雄数据文件不存在: {file_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._champion_data = ChampionDataModel(**data)
        self._champions = self._champion_data.data
        
        print(f"成功加载 {len(self._champions)} 个英雄数据")
        return self._champion_data
    
    def get_all_champions(self) -> Dict[str, ChampionModel]:
        return self._champions
    
    def get_champion_by_id(self, champion_id: str) -> Optional[ChampionModel]:
        return self._champions.get(champion_id)
    
    def get_champion_by_name(self, name: str) -> Optional[ChampionModel]:
        for champion in self._champions.values():
            if champion.name == name:
                return champion
        return None
    
    def search_champions(self, keyword: str) -> Dict[str, ChampionModel]:
        results = {}
        keyword_lower = keyword.lower()
        
        for champ_id, champion in self._champions.items():
            if (keyword_lower in champion.name.lower() or 
                keyword_lower in champion.title.lower() or
                keyword_lower in champion.id.lower()):
                results[champ_id] = champion
        
        return results
    
    def get_champions_by_tag(self, tag: str) -> Dict[str, ChampionModel]:
        results = {}
        
        for champ_id, champion in self._champions.items():
            if tag in champion.tags:
                results[champ_id] = champion
        
        return results
    
    def get_champion_count(self) -> int:
        return len(self._champions)
    
    def get_version(self) -> str:
        return self._champion_data.version if self._champion_data else ""


champion_service = ChampionService()

