"""
英雄相关路由
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from services.champion_service import champion_service
from database import get_session
from models import User, ChampionFavorite

router = APIRouter(prefix="/champions", tags=["champions"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def champions_list(request: Request):
    """英雄列表页面"""
    user = request.session.get('user')
    champions = list(champion_service.get_all_champions().values())
    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "user": user,
            "champions": champions,
            "selected_champion": None
        }
    )


@router.get("/{champion_id}", response_class=HTMLResponse)
async def champion_detail(request: Request, champion_id: str, session: Session = Depends(get_session)):
    """英雄详情页面"""
    user = request.session.get('user')
    champions = list(champion_service.get_all_champions().values())
    selected_champion = champion_service.get_champion_by_id(champion_id)

    if not selected_champion:
        return templates.TemplateResponse(
            request=request,
            name="champions.html",
            context={
                "user": user,
                "champions": champions,
                "selected_champion": None,
                "error": f"未找到英雄: {champion_id}"
            }
        )

    # 检查用户是否已收藏该英雄
    is_favorited = False
    if user:
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            favorite = session.exec(
                select(ChampionFavorite).where(
                    ChampionFavorite.user_id == db_user.id,
                    ChampionFavorite.champion_id == champion_id
                )
            ).first()
            is_favorited = favorite is not None

    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "user": user,
            "champions": champions,
            "selected_champion": selected_champion,
            "is_favorited": is_favorited
        }
    )


@router.post("/{champion_id}/favorite")
async def toggle_favorite(request: Request, champion_id: str, session: Session = Depends(get_session)):
    """切换英雄收藏状态"""
    user = request.session.get('user')
    champions = list(champion_service.get_all_champions().values())
    selected_champion = champion_service.get_champion_by_id(champion_id)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="champions.html",
            context={
                "user": user,
                "champions": champions,
                "selected_champion": selected_champion,
                "is_favorited": False,
                "error": "请先登录"
            }
        )

    # 查找用户
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return templates.TemplateResponse(
            request=request,
            name="champions.html",
            context={
                "user": user,
                "champions": champions,
                "selected_champion": selected_champion,
                "is_favorited": False,
                "error": "用户不存在"
            }
        )

    # 检查英雄是否存在
    if not selected_champion:
        return templates.TemplateResponse(
            request=request,
            name="champions.html",
            context={
                "user": user,
                "champions": champions,
                "selected_champion": None,
                "error": "英雄不存在"
            }
        )

    # 查找是否已收藏
    favorite = session.exec(
        select(ChampionFavorite).where(
            ChampionFavorite.user_id == db_user.id,
            ChampionFavorite.champion_id == champion_id
        )
    ).first()

    if favorite:
        # 已收藏，取消收藏
        session.delete(favorite)
        session.commit()
        message = "已取消收藏"
        is_favorited = False
    else:
        # 未收藏，添加收藏
        new_favorite = ChampionFavorite(
            user_id=db_user.id,
            champion_id=champion_id
        )
        session.add(new_favorite)
        session.commit()
        message = "收藏成功"
        is_favorited = True

    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "user": user,
            "champions": champions,
            "selected_champion": selected_champion,
            "is_favorited": is_favorited,
            "success": message
        }
    )

