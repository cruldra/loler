"""
装备相关路由
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from services.item_service import item_service
from services.champion_service import champion_service
from database import get_session
from models import User, ItemBuild
from datetime import datetime

router = APIRouter(prefix="/items", tags=["items"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def items_list(request: Request):
    """装备列表页面"""
    user = request.session.get('user')
    items_dict = item_service.get_purchasable_items()

    # 转换为列表并按价格排序
    items_list = [{"id": item_id, "item": item} for item_id, item in items_dict.items()]
    items_list.sort(key=lambda x: x["item"].gold.total)

    version = item_service.get_version()

    return templates.TemplateResponse(
        request=request,
        name="items/list.html",
        context={
            "user": user,
            "items": items_list,
            "version": version,
            "selected_item": None,
            "tag_translations": item_service.get_tag_translations()
        }
    )


@router.get("/builds", response_class=HTMLResponse)
async def item_builds_page(request: Request, edit: int = None, session: Session = Depends(get_session)):
    """装备配置方案页面"""
    user = request.session.get('user')
    items_dict = item_service.get_purchasable_items()

    items_list = [{"id": item_id, "item": item} for item_id, item in items_dict.items()]
    items_list.sort(key=lambda x: x["item"].gold.total)

    version = item_service.get_version()
    edit_build = None

    # 获取所有英雄列表
    champions = list(champion_service.get_all_champions().values())
    champions.sort(key=lambda x: x.name)

    if user and edit:
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            edit_build = session.exec(
                select(ItemBuild).where(
                    ItemBuild.id == edit,
                    ItemBuild.user_id == db_user.id
                )
            ).first()

    return templates.TemplateResponse(
        request=request,
        name="items/builds.html",
        context={
            "user": user,
            "items": items_list,
            "version": version,
            "edit_build": edit_build,
            "champions": champions,
            "tag_translations": item_service.get_tag_translations(),
            "map_translations": item_service.get_map_translations()
        }
    )


@router.get("/{item_id}", response_class=HTMLResponse)
async def item_detail(request: Request, item_id: str):
    """装备详情页面"""
    user = request.session.get('user')
    items_dict = item_service.get_purchasable_items()

    # 转换为列表并按价格排序
    items_list = [{"id": item_id, "item": item} for item_id, item in items_dict.items()]
    items_list.sort(key=lambda x: x["item"].gold.total)

    selected_item = item_service.get_item_by_id(item_id)
    version = item_service.get_version()
    all_items = item_service.get_all_items()

    if not selected_item:
        return templates.TemplateResponse(
            request=request,
            name="items/list.html",
            context={
                "user": user,
                "items": items_list,
                "version": version,
                "selected_item": None,
                "selected_item_id": None,
                "all_items": all_items,
                "tag_translations": item_service.get_tag_translations(),
                "error": f"未找到装备: {item_id}"
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="items/list.html",
        context={
            "user": user,
            "items": items_list,
            "version": version,
            "selected_item": selected_item,
            "selected_item_id": item_id,
            "all_items": all_items,
            "tag_translations": item_service.get_tag_translations()
        }
    )


@router.post("/builds/save")
async def save_item_build(request: Request, session: Session = Depends(get_session)):
    """保存装备配置方案"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login', status_code=303)

    form_data = await request.form()

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url='/login', status_code=303)

    build_id = form_data.get('build_id')

    if build_id:
        build = session.exec(
            select(ItemBuild).where(
                ItemBuild.id == int(build_id),
                ItemBuild.user_id == db_user.id
            )
        ).first()

        if not build:
            return RedirectResponse(url='/profile#item-builds', status_code=303)

        build.name = form_data.get('name', build.name)
        build.description = form_data.get('description')
        build.champion_id = form_data.get('champion_id')
        build.item_slot1 = form_data.get('item_slot1')
        build.item_slot2 = form_data.get('item_slot2')
        build.item_slot3 = form_data.get('item_slot3')
        build.item_slot4 = form_data.get('item_slot4')
        build.item_slot5 = form_data.get('item_slot5')
        build.item_slot6 = form_data.get('item_slot6')
        build.updated_at = datetime.now()
    else:
        build = ItemBuild(
            user_id=db_user.id,
            name=form_data.get('name', '新的配装方案'),
            description=form_data.get('description'),
            champion_id=form_data.get('champion_id'),
            item_slot1=form_data.get('item_slot1'),
            item_slot2=form_data.get('item_slot2'),
            item_slot3=form_data.get('item_slot3'),
            item_slot4=form_data.get('item_slot4'),
            item_slot5=form_data.get('item_slot5'),
            item_slot6=form_data.get('item_slot6')
        )
        session.add(build)

    session.commit()

    return RedirectResponse(url='/profile#item-builds', status_code=303)


@router.post("/builds/delete/{build_id}")
async def delete_item_build(request: Request, build_id: int, session: Session = Depends(get_session)):
    """删除装备配置方案"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login', status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url='/login', status_code=303)

    build = session.exec(
        select(ItemBuild).where(
            ItemBuild.id == build_id,
            ItemBuild.user_id == db_user.id
        )
    ).first()

    if build:
        session.delete(build)
        session.commit()

    return RedirectResponse(url='/profile#item-builds', status_code=303)

