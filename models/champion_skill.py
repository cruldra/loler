"""
英雄技能详情数据库模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text
from datetime import datetime


class ChampionSkill(SQLModel, table=True):
    """英雄技能详情表"""
    __tablename__ = "champion_skills"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="技能详情ID")
    user_id: int = Field(..., foreign_key="users.id", index=True, description="用户ID")
    champion_id: str = Field(..., index=True, description="英雄ID")
    skill_type: str = Field(..., description="技能类型(passive/Q/W/E/R)")
    
    # 图片相关
    image_path: Optional[str] = Field(default=None, description="上传的技能图片路径")
    
    # OCR识别的详细介绍
    ocr_description: Optional[str] = Field(default=None, sa_column=Column(Text), description="OCR识别的技能详细介绍")
    
    # 个人见解
    personal_notes: Optional[str] = Field(default=None, sa_column=Column(Text), description="个人见解(Markdown格式)")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

