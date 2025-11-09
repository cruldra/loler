"""
装备对比路由
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session, select
from services.item_service import item_service
from services.equipment_comparison_service import equipment_comparison_service
from database import get_session
from models import User, EquipmentComparison
import json

router = APIRouter(prefix="/tools", tags=["tools"])

templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


@router.get("/equipment-comparison", response_class=HTMLResponse)
async def equipment_comparison_page(request: Request):
    """装备对比页面"""
    user = request.session.get('user')

    # 获取所有可购买的装备
    items_dict = item_service.get_purchasable_items()
    items_list = [{"id": item_id, "item": item} for item_id, item in items_dict.items()]
    items_list.sort(key=lambda x: x["item"].gold.total)

    version = item_service.get_version()

    # 获取标签和地图翻译
    tag_translations = item_service.get_tag_translations()
    map_translations = item_service.get_map_translations()

    # 收集所有使用的标签
    all_tags = set()
    for item_data in items_list:
        all_tags.update(item_data["item"].tags)

    # 过滤掉不需要显示的标签
    excluded_tags = {"Lane", "Consumable", "Trinket", "Boots"}
    filtered_tags = [tag for tag in all_tags if tag not in excluded_tags]

    template = env.get_template("tools/equipment_comparison.html")
    html_content = template.render(
        request=request,
        user=user,
        items=items_list,
        version=version,
        tag_translations=tag_translations,
        map_translations=map_translations,
        available_tags=sorted(filtered_tags)
    )

    return HTMLResponse(content=html_content)


@router.get("/equipment-comparison/item/{item_id}", response_class=HTMLResponse)
async def get_item_comparisons(request: Request, item_id: str, session: Session = Depends(get_session)):
    """获取某个装备的所有对比报告"""
    user = request.session.get('user')

    if not user:
        return HTMLResponse(content="<p>请先登录</p>", status_code=401)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return HTMLResponse(content="<p>用户不存在</p>", status_code=404)

    # 查询该装备相关的所有对比报告（作为item1或item2）
    comparisons = session.exec(
        select(EquipmentComparison).where(
            EquipmentComparison.user_id == db_user.id,
            (EquipmentComparison.item1_id == item_id) | (EquipmentComparison.item2_id == item_id)
        ).order_by(EquipmentComparison.created_at.desc())
    ).all()

    # 获取装备信息
    item = item_service.get_item_by_id(item_id)
    version = item_service.get_version()

    # 渲染模板
    template = env.get_template("tools/item_comparisons.html")
    html_content = template.render(
        request=request,
        user=user,
        item=item,
        item_id=item_id,
        comparisons=comparisons,
        version=version
    )

    return HTMLResponse(content=html_content)


@router.get("/equipment-comparison/{comparison_id}")
async def get_comparison_detail(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """获取对比报告详情"""
    user = request.session.get('user')

    if not user:
        return JSONResponse(content={"error": "未登录"}, status_code=401)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return JSONResponse(content={"error": "用户不存在"}, status_code=404)

    # 查询对比报告
    comparison = session.exec(
        select(EquipmentComparison).where(
            EquipmentComparison.id == comparison_id,
            EquipmentComparison.user_id == db_user.id
        )
    ).first()

    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    # 解析stats_comparison JSON
    stats_comparison = json.loads(comparison.stats_comparison)

    # 获取装备信息
    item1 = item_service.get_item_by_id(comparison.item1_id)
    item2 = item_service.get_item_by_id(comparison.item2_id)
    version = item_service.get_version()

    return JSONResponse(content={
        "id": comparison.id,
        "item1_id": comparison.item1_id,
        "item1_name": comparison.item1_name,
        "item2_id": comparison.item2_id,
        "item2_name": comparison.item2_name,
        "ai_commentary": comparison.ai_commentary,
        "ai_tags": comparison.ai_tags.split(',') if comparison.ai_tags else [],
        "stats_comparison": stats_comparison,
        "created_at": comparison.created_at.strftime('%Y-%m-%d %H:%M'),
        "version": version
    })


@router.delete("/equipment-comparison/{comparison_id}")
async def delete_comparison(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """删除对比报告"""
    user = request.session.get('user')

    if not user:
        return JSONResponse(content={"error": "未登录"}, status_code=401)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return JSONResponse(content={"error": "用户不存在"}, status_code=404)

    # 查询对比报告
    comparison = session.exec(
        select(EquipmentComparison).where(
            EquipmentComparison.id == comparison_id,
            EquipmentComparison.user_id == db_user.id
        )
    ).first()

    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    # 删除对比报告
    session.delete(comparison)
    session.commit()

    return JSONResponse(content={"success": True})


@router.post("/equipment-comparison/compare", response_class=HTMLResponse)
async def compare_equipment(request: Request, session: Session = Depends(get_session)):
    """对比两个装备并返回AI点评"""
    user = request.session.get('user')
    data = await request.json()
    item1_id = data.get("item1_id")
    item2_id = data.get("item2_id")

    if not item1_id or not item2_id:
        return HTMLResponse(content="<p>请选择两个装备进行对比</p>", status_code=400)

    item1 = item_service.get_item_by_id(item1_id)
    item2 = item_service.get_item_by_id(item2_id)

    if not item1 or not item2:
        return HTMLResponse(content="<p>装备不存在</p>", status_code=404)

    # 计算属性差异
    stats_comparison = {
        "attack_damage": {
            "item1": item1.stats.FlatPhysicalDamageMod or 0,
            "item2": item2.stats.FlatPhysicalDamageMod or 0,
            "diff": (item2.stats.FlatPhysicalDamageMod or 0) - (item1.stats.FlatPhysicalDamageMod or 0)
        },
        "ability_power": {
            "item1": item1.stats.FlatMagicDamageMod or 0,
            "item2": item2.stats.FlatMagicDamageMod or 0,
            "diff": (item2.stats.FlatMagicDamageMod or 0) - (item1.stats.FlatMagicDamageMod or 0)
        },
        "armor": {
            "item1": item1.stats.FlatArmorMod or 0,
            "item2": item2.stats.FlatArmorMod or 0,
            "diff": (item2.stats.FlatArmorMod or 0) - (item1.stats.FlatArmorMod or 0)
        },
        "magic_resist": {
            "item1": item1.stats.FlatSpellBlockMod or 0,
            "item2": item2.stats.FlatSpellBlockMod or 0,
            "diff": (item2.stats.FlatSpellBlockMod or 0) - (item1.stats.FlatSpellBlockMod or 0)
        },
        "health": {
            "item1": item1.stats.FlatHPPoolMod or 0,
            "item2": item2.stats.FlatHPPoolMod or 0,
            "diff": (item2.stats.FlatHPPoolMod or 0) - (item1.stats.FlatHPPoolMod or 0)
        },
        "crit_chance": {
            "item1": (item1.stats.FlatCritChanceMod or 0) * 100,
            "item2": (item2.stats.FlatCritChanceMod or 0) * 100,
            "diff": ((item2.stats.FlatCritChanceMod or 0) - (item1.stats.FlatCritChanceMod or 0)) * 100
        },
        "attack_speed": {
            "item1": (item1.stats.PercentAttackSpeedMod or 0) * 100,
            "item2": (item2.stats.PercentAttackSpeedMod or 0) * 100,
            "diff": ((item2.stats.PercentAttackSpeedMod or 0) - (item1.stats.PercentAttackSpeedMod or 0)) * 100
        },
        "price": {
            "item1": item1.gold.total,
            "item2": item2.gold.total,
            "diff": item2.gold.total - item1.gold.total
        }
    }

    # 使用CrewAI进行AI点评
    ai_result = equipment_comparison_service.compare_items(
        item1=item1,
        item2=item2,
        stats_comparison=stats_comparison
    )

    # 保存对比报告到数据库
    if user:
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            comparison = EquipmentComparison(
                user_id=db_user.id,
                item1_id=item1_id,
                item1_name=item1.name,
                item2_id=item2_id,
                item2_name=item2.name,
                ai_commentary=ai_result["comment"],
                ai_tags=",".join(ai_result["tags"]),
                stats_comparison=json.dumps(stats_comparison, ensure_ascii=False)
            )
            session.add(comparison)
            session.commit()

    # 渲染结果模板
    template = env.get_template("tools/comparison_result.html")
    html_content = template.render(
        item1=item1,
        item2=item2,
        stats_comparison=stats_comparison,
        ai_commentary=ai_result["comment"],
        ai_tags=ai_result["tags"]
    )

    return HTMLResponse(content=html_content)

