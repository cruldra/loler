"""
符文对比分析路由
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session
from datetime import datetime

from database import get_session
from models import User, RuneComparison
from services.rune_service import rune_service
from services.rune_comparison_service import rune_comparison_service
from sqlmodel import select

router = APIRouter(prefix="/tools/rune-comparison", tags=["rune_comparison"])

templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


def require_login(request: Request):
    """检查用户是否登录"""
    user = request.session.get('user')
    if not user:
        return None
    return user


@router.get("/", response_class=HTMLResponse)
async def rune_comparison_page(request: Request):
    """符文对比分析页面"""
    user = require_login(request)
    if not user:
        template = env.get_template("login.html")
        html_content = template.render(
            request=request,
            error="请先登录"
        )
        return HTMLResponse(content=html_content)
    
    # 获取所有符文系
    rune_trees = list(rune_service.get_all_trees().values())
    version = rune_service.get_version()
    
    template = env.get_template("tools/rune_comparison.html")
    html_content = template.render(
        request=request,
        user=user,
        rune_trees=rune_trees,
        version=version
    )
    
    return HTMLResponse(content=html_content)


@router.post("/compare", response_class=HTMLResponse)
async def compare_runes(request: Request, session: Session = Depends(get_session)):
    """执行符文对比分析并返回HTML片段"""
    user = require_login(request)
    data = await request.json()
    rune1_id = data.get("rune1_id")
    rune2_id = data.get("rune2_id")
    
    if not rune1_id or not rune2_id:
        return HTMLResponse(content="<p>请选择两个符文进行对比</p>", status_code=400)
    
    # 获取符文数据
    rune1 = rune_service.get_rune_by_id(int(rune1_id))
    rune2 = rune_service.get_rune_by_id(int(rune2_id))
    
    if not rune1 or not rune2:
        return HTMLResponse(content="<p>符文不存在</p>", status_code=404)
    
    # 获取符文所属的符文系
    rune1_tree = None
    rune2_tree = None
    for tree in rune_service.get_all_trees().values():
        for slot in tree.slots:
            for rune in slot.runes:
                if rune.id == rune1.id:
                    rune1_tree = tree
                if rune.id == rune2.id:
                    rune2_tree = tree
    
    # 判断是否为基石符文
    rune1_is_keystone = False
    rune2_is_keystone = False
    if rune1_tree:
        rune1_is_keystone = rune1.id in [r.id for r in rune1_tree.slots[0].runes]
    if rune2_tree:
        rune2_is_keystone = rune2.id in [r.id for r in rune2_tree.slots[0].runes]

    # 使用AI服务生成对比分析
    ai_result = rune_comparison_service.compare_runes(
        rune1=rune1,
        rune2=rune2,
        rune1_tree=rune1_tree,
        rune2_tree=rune2_tree,
        rune1_is_keystone=rune1_is_keystone,
        rune2_is_keystone=rune2_is_keystone
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
            comparison = RuneComparison(
                user_id=db_user.id,
                rune1_id=str(rune1.id),
                rune1_name=rune1.name,
                rune2_id=str(rune2.id),
                rune2_name=rune2.name,
                ai_commentary=ai_result["comment"],
                ai_tags=",".join(ai_result["tags"])
            )
            session.add(comparison)
            session.commit()
    
    # 渲染结果模板片段
    version = rune_service.get_version()
    template = env.get_template("tools/rune_comparison_result.html")
    html_content = template.render(
        rune1=rune1,
        rune2=rune2,
        rune1_tree=rune1_tree,
        rune2_tree=rune2_tree,
        rune1_is_keystone=rune1_is_keystone,
        rune2_is_keystone=rune2_is_keystone,
        ai_commentary=ai_result["comment"],
        ai_tags=ai_result["tags"],
        version=version
    )

    return HTMLResponse(content=html_content)


@router.get("/history", response_class=HTMLResponse)
async def rune_comparison_history(request: Request, session: Session = Depends(get_session)):
    """符文对比历史记录页面"""
    user = require_login(request)
    if not user:
        template = env.get_template("login.html")
        html_content = template.render(
            request=request,
            error="请先登录"
        )
        return HTMLResponse(content=html_content)

    # 获取当前用户
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return HTMLResponse(content="<p>用户不存在</p>", status_code=404)

    # 获取用户的所有符文对比记录，按创建时间倒序
    comparisons = session.exec(
        select(RuneComparison)
        .where(RuneComparison.user_id == db_user.id)
        .order_by(RuneComparison.created_at.desc())
    ).all()

    # 为每个对比记录添加符文详细信息
    comparisons_with_details = []
    for comparison in comparisons:
        rune1 = rune_service.get_rune_by_id(int(comparison.rune1_id))
        rune2 = rune_service.get_rune_by_id(int(comparison.rune2_id))

        # 获取符文所属的符文系和是否为基石符文
        rune1_tree = None
        rune2_tree = None
        rune1_is_keystone = False
        rune2_is_keystone = False

        for tree in rune_service.get_all_trees().values():
            for slot_idx, slot in enumerate(tree.slots):
                for rune in slot.runes:
                    if rune.id == int(comparison.rune1_id):
                        rune1_tree = tree
                        rune1_is_keystone = (slot_idx == 0)
                    if rune.id == int(comparison.rune2_id):
                        rune2_tree = tree
                        rune2_is_keystone = (slot_idx == 0)

        comparisons_with_details.append({
            'comparison': comparison,
            'rune1': rune1,
            'rune2': rune2,
            'rune1_tree': rune1_tree,
            'rune2_tree': rune2_tree,
            'rune1_is_keystone': rune1_is_keystone,
            'rune2_is_keystone': rune2_is_keystone
        })

    version = rune_service.get_version()

    template = env.get_template("tools/rune_comparison_history.html")
    html_content = template.render(
        request=request,
        user=user,
        comparisons_with_details=comparisons_with_details,
        version=version
    )

    return HTMLResponse(content=html_content)


@router.get("/{comparison_id}", response_class=JSONResponse)
async def get_comparison_detail(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """获取对比详情"""
    user = require_login(request)
    if not user:
        return JSONResponse(content={"error": "请先登录"}, status_code=401)

    comparison = session.get(RuneComparison, comparison_id)
    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    # 获取符文信息
    rune1 = rune_service.get_rune_by_id(int(comparison.rune1_id))
    rune2 = rune_service.get_rune_by_id(int(comparison.rune2_id))

    # 获取符文所属的符文系
    rune1_tree = None
    rune2_tree = None
    rune1_is_keystone = False
    rune2_is_keystone = False

    for tree in rune_service.get_all_trees().values():
        for slot_idx, slot in enumerate(tree.slots):
            for rune in slot.runes:
                if rune.id == rune1.id:
                    rune1_tree = tree
                    rune1_is_keystone = (slot_idx == 0)
                if rune.id == rune2.id:
                    rune2_tree = tree
                    rune2_is_keystone = (slot_idx == 0)

    version = rune_service.get_version()

    return JSONResponse(content={
        "rune1": {
            "id": rune1.id,
            "name": rune1.name,
            "icon": rune1.icon,
            "tree": rune1_tree.name if rune1_tree else "未知",
            "tree_key": rune1_tree.key if rune1_tree else "",
            "is_keystone": rune1_is_keystone
        },
        "rune2": {
            "id": rune2.id,
            "name": rune2.name,
            "icon": rune2.icon,
            "tree": rune2_tree.name if rune2_tree else "未知",
            "tree_key": rune2_tree.key if rune2_tree else "",
            "is_keystone": rune2_is_keystone
        },
        "ai_commentary": comparison.ai_commentary,
        "ai_tags": comparison.ai_tags.split(',') if comparison.ai_tags else [],
        "created_at": comparison.created_at.strftime('%Y-%m-%d %H:%M'),
        "version": version
    })


@router.delete("/{comparison_id}", response_class=JSONResponse)
async def delete_comparison(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """删除对比报告"""
    user = require_login(request)
    if not user:
        return JSONResponse(content={"error": "请先登录"}, status_code=401)

    comparison = session.get(RuneComparison, comparison_id)
    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    session.delete(comparison)
    session.commit()

    return JSONResponse(content={"success": True})

