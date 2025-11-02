"""
符文数据服务
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from schemas.rune import RuneTreeModel, RuneModel


class RuneService:
    """符文数据服务类"""
    
    def __init__(self):
        self.rune_trees: Dict[int, RuneTreeModel] = {}
        self.rune_trees_by_key: Dict[str, RuneTreeModel] = {}
        self.all_runes: Dict[int, RuneModel] = {}
        self.version: str = ""
    
    def load_runes(self, file_path: str = "dragontail/15.21.1/data/zh_CN/runesReforged.json"):
        """
        加载符文数据
        
        Args:
            file_path: 符文数据文件路径
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"符文数据文件不存在: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空现有数据
            self.rune_trees.clear()
            self.rune_trees_by_key.clear()
            self.all_runes.clear()
            
            # 解析符文系数据
            for tree_data in data:
                tree = RuneTreeModel(**tree_data)
                self.rune_trees[tree.id] = tree
                self.rune_trees_by_key[tree.key] = tree
                
                # 收集所有符文到扁平字典
                for slot in tree.slots:
                    for rune in slot.runes:
                        self.all_runes[rune.id] = rune
            
            # 从路径提取版本号
            self.version = path.parts[-4] if len(path.parts) >= 4 else "unknown"
            
            print(f"成功加载 {len(self.rune_trees)} 个符文系, 共 {len(self.all_runes)} 个符文")
            
        except Exception as e:
            print(f"加载符文数据失败: {e}")
            raise
    
    def get_all_trees(self) -> Dict[int, RuneTreeModel]:
        """
        获取所有符文系
        
        Returns:
            符文系字典 {id: RuneTreeModel}
        """
        return self.rune_trees
    
    def get_tree_by_id(self, tree_id: int) -> Optional[RuneTreeModel]:
        """
        根据ID获取符文系
        
        Args:
            tree_id: 符文系ID
            
        Returns:
            符文系模型或None
        """
        return self.rune_trees.get(tree_id)
    
    def get_tree_by_key(self, key: str) -> Optional[RuneTreeModel]:
        """
        根据键名获取符文系
        
        Args:
            key: 符文系英文键名(如 "Domination", "Precision")
            
        Returns:
            符文系模型或None
        """
        return self.rune_trees_by_key.get(key)
    
    def get_rune_by_id(self, rune_id: int) -> Optional[RuneModel]:
        """
        根据ID获取符文
        
        Args:
            rune_id: 符文ID
            
        Returns:
            符文模型或None
        """
        return self.all_runes.get(rune_id)
    
    def search_runes(self, keyword: str) -> List[RuneModel]:
        """
        搜索符文
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            符文列表
        """
        keyword = keyword.lower()
        results = []
        
        for rune in self.all_runes.values():
            if (keyword in rune.name.lower() or 
                keyword in rune.key.lower() or
                keyword in rune.shortDesc.lower()):
                results.append(rune)
        
        return results
    
    def get_runes_by_tree(self, tree_id: int) -> List[RuneModel]:
        """
        获取指定符文系的所有符文
        
        Args:
            tree_id: 符文系ID
            
        Returns:
            符文列表
        """
        tree = self.get_tree_by_id(tree_id)
        if not tree:
            return []
        
        runes = []
        for slot in tree.slots:
            runes.extend(slot.runes)
        
        return runes
    
    def get_keystone_runes(self) -> List[RuneModel]:
        """
        获取所有基石符文(每个符文系第一行的符文)
        
        Returns:
            基石符文列表
        """
        keystones = []
        
        for tree in self.rune_trees.values():
            if tree.slots and tree.slots[0].runes:
                keystones.extend(tree.slots[0].runes)
        
        return keystones
    
    def get_version(self) -> str:
        """
        获取符文数据版本
        
        Returns:
            版本号字符串
        """
        return self.version


# 创建全局单例
rune_service = RuneService()

