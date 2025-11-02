"""
装备服务
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from schemas.item import ItemModel, ItemDataModel


class ItemService:
    def __init__(self):
        self._item_data: Optional[ItemDataModel] = None
        self._items: Dict[str, ItemModel] = {}
    
    def load_items(self, file_path: str = "dragontail/15.21.1/data/zh_CN/item.json"):
        """
        加载装备数据
        
        Args:
            file_path: 装备数据文件路径
        """
        json_path = Path(file_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"装备数据文件不存在: {file_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._item_data = ItemDataModel(**data)
        self._items = self._item_data.data
        
        print(f"成功加载 {len(self._items)} 个装备数据")
        return self._item_data
    
    def get_all_items(self) -> Dict[str, ItemModel]:
        """
        获取所有装备
        
        Returns:
            装备字典 {id: ItemModel}
        """
        return self._items
    
    def get_item_by_id(self, item_id: str) -> Optional[ItemModel]:
        """
        根据ID获取装备
        
        Args:
            item_id: 装备ID
            
        Returns:
            装备模型或None
        """
        return self._items.get(item_id)
    
    def search_items(self, keyword: str) -> Dict[str, ItemModel]:
        """
        搜索装备
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的装备字典
        """
        results = {}
        keyword_lower = keyword.lower()
        
        for item_id, item in self._items.items():
            if (keyword_lower in item.name.lower() or 
                keyword_lower in item.plaintext.lower() or
                keyword_lower in item.colloq.lower()):
                results[item_id] = item
        
        return results
    
    def get_items_by_tag(self, tag: str) -> Dict[str, ItemModel]:
        """
        根据标签获取装备
        
        Args:
            tag: 标签名称
            
        Returns:
            匹配的装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if tag in item.tags:
                results[item_id] = item
        
        return results
    
    def get_purchasable_items(self) -> Dict[str, ItemModel]:
        """
        获取可购买的装备（排除消耗品和隐藏装备）
        
        Returns:
            可购买的装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if (item.gold.purchasable and 
                item.inStore and 
                not item.hideFromAll and
                not item.consumed and
                not item.requiredChampion):
                results[item_id] = item
        
        return results
    
    def get_starter_items(self) -> Dict[str, ItemModel]:
        """
        获取起始装备
        
        Returns:
            起始装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if "Lane" in item.tags and item.gold.total <= 500:
                results[item_id] = item
        
        return results
    
    def get_boots(self) -> Dict[str, ItemModel]:
        """
        获取鞋子装备
        
        Returns:
            鞋子装备字典
        """
        return self.get_items_by_tag("Boots")
    
    def get_legendary_items(self) -> Dict[str, ItemModel]:
        """
        获取传说装备（高级装备）
        
        Returns:
            传说装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if (item.gold.total >= 2500 and 
                item.gold.purchasable and 
                item.inStore and
                not item.hideFromAll and
                not item.consumed):
                results[item_id] = item
        
        return results
    
    def get_basic_items(self) -> Dict[str, ItemModel]:
        """
        获取基础装备
        
        Returns:
            基础装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if (item.depth == 1 and 
                item.gold.purchasable and 
                item.inStore and
                not item.hideFromAll and
                not item.consumed and
                "Lane" not in item.tags):
                results[item_id] = item
        
        return results
    
    def get_epic_items(self) -> Dict[str, ItemModel]:
        """
        获取史诗装备（中级装备）
        
        Returns:
            史诗装备字典
        """
        results = {}
        
        for item_id, item in self._items.items():
            if (item.depth == 2 and 
                item.gold.purchasable and 
                item.inStore and
                not item.hideFromAll and
                not item.consumed):
                results[item_id] = item
        
        return results
    
    def get_item_count(self) -> int:
        """
        获取装备总数
        
        Returns:
            装备数量
        """
        return len(self._items)
    
    def get_version(self) -> str:
        """
        获取数据版本
        
        Returns:
            版本号
        """
        return self._item_data.version if self._item_data else ""


item_service = ItemService()

