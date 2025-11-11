"""
英雄技能详情数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChampionSkillCreate(BaseModel):
    """创建技能详情请求"""
    champion_id: str = Field(..., description="英雄ID")
    skill_type: str = Field(..., description="技能类型(passive/Q/W/E/R)")
    personal_notes: Optional[str] = Field(default=None, description="个人见解(Markdown格式)")


class ChampionSkillUpdate(BaseModel):
    """更新技能详情请求"""
    ocr_description: Optional[str] = Field(default=None, description="OCR识别的技能详细介绍")
    personal_notes: Optional[str] = Field(default=None, description="个人见解(Markdown格式)")


class ChampionSkillResponse(BaseModel):
    """技能详情响应"""
    id: int = Field(..., description="技能详情ID")
    user_id: int = Field(..., description="用户ID")
    champion_id: str = Field(..., description="英雄ID")
    skill_type: str = Field(..., description="技能类型(passive/Q/W/E/R)")
    image_path: Optional[str] = Field(default=None, description="上传的技能图片路径")
    ocr_description: Optional[str] = Field(default=None, description="OCR识别的技能详细介绍")
    personal_notes: Optional[str] = Field(default=None, description="个人见解(Markdown格式)")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

