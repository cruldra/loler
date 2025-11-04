"""
野怪相关路由
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.monster_service import monster_service

router = APIRouter(prefix="/monsters", tags=["monsters"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def monsters_page(request: Request):
    """野怪数据页面"""
    user = request.session.get('user')
    monsters = monster_service.get_all_monsters()

    return templates.TemplateResponse(
        request=request,
        name="monsters.html",
        context={
            "user": user,
            "monsters": monsters
        }
    )

