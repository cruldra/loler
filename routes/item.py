"""
装备相关路由
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.item_service import item_service

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
            "selected_item": None
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
            "all_items": all_items
        }
    )

