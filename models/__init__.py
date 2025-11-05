"""
数据库模型定义
"""
from .user import User
from .rune_page import RunePage
from .team_composition import TeamComposition
from .champion_favorite import ChampionFavorite
from .highlight_video import HighlightVideo
from .champion_tip import ChampionTip
from .item_build import ItemBuild
from .replay import Replay

__all__ = [
    "User",
    "RunePage",
    "TeamComposition",
    "ChampionFavorite",
    "HighlightVideo",
    "ChampionTip",
    "ItemBuild",
    "Replay"
]
