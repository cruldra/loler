"""
收集装备标签并生成英文到中文的映射
"""
import json
from pathlib import Path

# 装备标签的英文到中文映射
TAG_TRANSLATIONS = {
    "Boots": "鞋子",
    "ManaRegen": "法力回复",
    "HealthRegen": "生命回复",
    "Health": "生命值",
    "CriticalStrike": "暴击",
    "SpellDamage": "法术伤害",
    "Mana": "法力值",
    "Armor": "护甲",
    "SpellBlock": "魔法抗性",
    "LifeSteal": "生命偷取",
    "SpellVamp": "法术吸血",
    "Jungle": "打野",
    "Lane": "对线",
    "Damage": "伤害",
    "AttackSpeed": "攻击速度",
    "OnHit": "攻击特效",
    "Trinket": "饰品",
    "Active": "主动",
    "Consumable": "消耗品",
    "Stealth": "隐身",
    "Vision": "视野",
    "NonbootsMovement": "移动速度",
    "Tenacity": "韧性",
    "ArmorPenetration": "护甲穿透",
    "MagicPenetration": "法术穿透",
    "CooldownReduction": "冷却缩减",
    "AbilityHaste": "技能急速",
    "GoldPer": "金币收入",
    "Aura": "光环",
    "Slow": "减速",
    "MagicResist": "魔法抗性"
}


def collect_tags_from_items():
    """从装备数据中收集所有标签"""
    item_file = Path("dragontail/15.21.1/data/zh_CN/item.json")
    
    if not item_file.exists():
        print(f"错误: 文件不存在 {item_file}")
        return
    
    with open(item_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 收集所有唯一的标签
    all_tags = set()
    items_data = data.get("data", {})
    
    for item_id, item in items_data.items():
        tags = item.get("tags", [])
        all_tags.update(tags)
    
    print(f"找到 {len(all_tags)} 个唯一标签:")
    for tag in sorted(all_tags):
        translation = TAG_TRANSLATIONS.get(tag, tag)
        print(f"  {tag}: {translation}")
    
    # 检查是否有未翻译的标签
    untranslated = all_tags - set(TAG_TRANSLATIONS.keys())
    if untranslated:
        print(f"\n警告: 以下标签未翻译:")
        for tag in sorted(untranslated):
            print(f"  {tag}")
    
    # 保存到JSON文件
    output_file = Path("data/item_tag_translations.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(TAG_TRANSLATIONS, f, ensure_ascii=False, indent=2)
    
    print(f"\n标签翻译已保存到: {output_file}")


if __name__ == "__main__":
    collect_tags_from_items()

