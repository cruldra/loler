"""
阵容配置数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class TeamComposition(SQLModel, table=True):
    """阵容配置表"""
    __tablename__ = "team_compositions"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="阵容配置ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    name: str = Field(..., description="阵容名称")
    description: Optional[str] = Field(default=None, description="阵容描述")
    
    # 队伍1配置
    team1_player1_champion: Optional[str] = Field(default=None, description="队伍1玩家1英雄ID")
    team1_player1_role: Optional[str] = Field(default=None, description="队伍1玩家1位置")

    team1_player2_champion: Optional[str] = Field(default=None, description="队伍1玩家2英雄ID")
    team1_player2_role: Optional[str] = Field(default=None, description="队伍1玩家2位置")

    team1_player3_champion: Optional[str] = Field(default=None, description="队伍1玩家3英雄ID")
    team1_player3_role: Optional[str] = Field(default=None, description="队伍1玩家3位置")

    team1_player4_champion: Optional[str] = Field(default=None, description="队伍1玩家4英雄ID")
    team1_player4_role: Optional[str] = Field(default=None, description="队伍1玩家4位置")

    team1_player5_champion: Optional[str] = Field(default=None, description="队伍1玩家5英雄ID")
    team1_player5_role: Optional[str] = Field(default=None, description="队伍1玩家5位置")

    # 队伍2配置
    team2_player1_champion: Optional[str] = Field(default=None, description="队伍2玩家1英雄ID")
    team2_player1_role: Optional[str] = Field(default=None, description="队伍2玩家1位置")

    team2_player2_champion: Optional[str] = Field(default=None, description="队伍2玩家2英雄ID")
    team2_player2_role: Optional[str] = Field(default=None, description="队伍2玩家2位置")

    team2_player3_champion: Optional[str] = Field(default=None, description="队伍2玩家3英雄ID")
    team2_player3_role: Optional[str] = Field(default=None, description="队伍2玩家3位置")

    team2_player4_champion: Optional[str] = Field(default=None, description="队伍2玩家4英雄ID")
    team2_player4_role: Optional[str] = Field(default=None, description="队伍2玩家4位置")

    team2_player5_champion: Optional[str] = Field(default=None, description="队伍2玩家5英雄ID")
    team2_player5_role: Optional[str] = Field(default=None, description="队伍2玩家5位置")

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

