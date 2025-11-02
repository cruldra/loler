"""
英雄相关路由
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.champion_service import champion_service

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
async def champion_detail(request: Request, champion_id: str):
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

    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "user": user,
            "champions": champions,
            "selected_champion": selected_champion
        }
    )

