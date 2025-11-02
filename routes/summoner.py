"""
召唤师技能相关路由
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.summoner_service import summoner_service

router = APIRouter(prefix="/summoner", tags=["summoner"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def summoner_list(request: Request):
    """召唤师技能列表页面"""

    # 获取用户信息
    user = request.session.get('user')

    # 获取所有召唤师技能
    summoner_spells = summoner_service.get_all_summoner_spells()

    # 按名称排序
    summoner_spells.sort(key=lambda x: x.name)

    version = summoner_service.get_version()

    return templates.TemplateResponse(
        "summoner/list.html",
        {
            "request": request,
            "user": user,
            "summoner_spells": summoner_spells,
            "version": version,
            "selected_spell": None
        }
    )


@router.get("/{spell_id}", response_class=HTMLResponse)
async def summoner_detail(request: Request, spell_id: str):
    """召唤师技能详情页面"""

    # 获取用户信息
    user = request.session.get('user')

    # 获取所有召唤师技能
    summoner_spells = summoner_service.get_all_summoner_spells()

    # 按名称排序
    summoner_spells.sort(key=lambda x: x.name)

    # 获取选中的技能
    selected_spell = summoner_service.get_summoner_spell_by_id(spell_id)
    version = summoner_service.get_version()

    if not selected_spell:
        return templates.TemplateResponse(
            "summoner/list.html",
            {
                "request": request,
                "user": user,
                "summoner_spells": summoner_spells,
                "version": version,
                "selected_spell": None,
                "error": f"未找到召唤师技能: {spell_id}"
            }
        )

    return templates.TemplateResponse(
        "summoner/list.html",
        {
            "request": request,
            "user": user,
            "summoner_spells": summoner_spells,
            "version": version,
            "selected_spell": selected_spell
        }
    )

