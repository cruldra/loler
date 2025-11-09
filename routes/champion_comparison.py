"""
英雄对比分析路由
"""
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session
from datetime import datetime

from database import get_session
from models import ChampionComparison, User
from services.champion_service import champion_service
from services.champion_comparison_service import champion_comparison_service
from sqlmodel import select
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/tools/champion-comparison", tags=["champion_comparison"])

templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


def require_login(request: Request):
    """检查用户是否登录"""
    user = request.session.get('user')
    if not user:
        return None
    return user


@router.get("/", response_class=HTMLResponse)
async def champion_comparison_page(request: Request):
    """英雄对比分析页面"""
    user = require_login(request)
    if not user:
        template = env.get_template("login.html")
        html_content = template.render(
            request=request,
            error="请先登录"
        )
        return HTMLResponse(content=html_content)

    # 获取所有英雄
    champions = list(champion_service.get_all_champions().values())
    version = champion_service.get_version()

    template = env.get_template("tools/champion_comparison.html")
    html_content = template.render(
        request=request,
        user=user,
        champions=champions,
        version=version
    )

    return HTMLResponse(content=html_content)


@router.post("/compare", response_class=HTMLResponse)
async def compare_champions(request: Request, session: Session = Depends(get_session)):
    """执行英雄对比分析并返回HTML片段"""
    user = require_login(request)
    data = await request.json()
    champion1_id = data.get("champion1_id")
    champion2_id = data.get("champion2_id")

    if not champion1_id or not champion2_id:
        return HTMLResponse(content="<p>请选择两个英雄进行对比</p>", status_code=400)

    # 获取英雄数据
    champion1 = champion_service.get_champion_by_id(champion1_id)
    champion2 = champion_service.get_champion_by_id(champion2_id)

    if not champion1 or not champion2:
        return HTMLResponse(content="<p>英雄不存在</p>", status_code=404)

    # 构建属性对比数据
    stats_comparison = {
        "hp": {"champion1": champion1.stats.hp, "champion2": champion2.stats.hp},
        "hp_per_level": {"champion1": champion1.stats.hpperlevel, "champion2": champion2.stats.hpperlevel},
        "mp": {"champion1": champion1.stats.mp, "champion2": champion2.stats.mp},
        "mp_per_level": {"champion1": champion1.stats.mpperlevel, "champion2": champion2.stats.mpperlevel},
        "attack_damage": {"champion1": champion1.stats.attackdamage, "champion2": champion2.stats.attackdamage},
        "attack_damage_per_level": {"champion1": champion1.stats.attackdamageperlevel, "champion2": champion2.stats.attackdamageperlevel},
        "attack_speed": {"champion1": champion1.stats.attackspeed, "champion2": champion2.stats.attackspeed},
        "attack_speed_per_level": {"champion1": champion1.stats.attackspeedperlevel, "champion2": champion2.stats.attackspeedperlevel},
        "attack_range": {"champion1": champion1.stats.attackrange, "champion2": champion2.stats.attackrange},
        "armor": {"champion1": champion1.stats.armor, "champion2": champion2.stats.armor},
        "armor_per_level": {"champion1": champion1.stats.armorperlevel, "champion2": champion2.stats.armorperlevel},
        "magic_resist": {"champion1": champion1.stats.spellblock, "champion2": champion2.stats.spellblock},
        "magic_resist_per_level": {"champion1": champion1.stats.spellblockperlevel, "champion2": champion2.stats.spellblockperlevel},
        "move_speed": {"champion1": champion1.stats.movespeed, "champion2": champion2.stats.movespeed},
        "difficulty": {"champion1": champion1.info.difficulty, "champion2": champion2.info.difficulty}
    }

    # 调用AI服务生成对比分析
    ai_commentary = champion_comparison_service.compare_champions(champion1, champion2)

    # 生成标签
    ai_tags = champion_comparison_service.generate_tags(ai_commentary)

    # 保存到数据库
    if user:
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            comparison = ChampionComparison(
                user_id=db_user.id,
                champion1_id=champion1_id,
                champion1_name=champion1.name,
                champion2_id=champion2_id,
                champion2_name=champion2.name,
                ai_commentary=ai_commentary,
                ai_tags=','.join(ai_tags),
                stats_comparison=json.dumps(stats_comparison, ensure_ascii=False),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(comparison)
            session.commit()

    # 渲染结果模板片段
    version = champion_service.get_version()
    template = env.get_template("tools/champion_comparison_result.html")
    html_content = template.render(
        champion1=champion1,
        champion2=champion2,
        stats_comparison=stats_comparison,
        ai_commentary=ai_commentary,
        ai_tags=ai_tags,
        version=version
    )

    return HTMLResponse(content=html_content)


@router.get("/champion/{champion_id}/comparisons", response_class=HTMLResponse)
async def get_champion_comparisons(champion_id: str, request: Request, session: Session = Depends(get_session)):
    """获取英雄相关的所有对比报告"""
    user = require_login(request)
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

    # 查询该英雄相关的所有对比报告（作为champion1或champion2）
    comparisons = session.exec(
        select(ChampionComparison).where(
            ChampionComparison.user_id == db_user.id,
            (ChampionComparison.champion1_id == champion_id) | (ChampionComparison.champion2_id == champion_id)
        ).order_by(ChampionComparison.created_at.desc())
    ).all()

    # 获取英雄信息
    champion = champion_service.get_champion_by_id(champion_id)
    version = champion_service.get_version()

    # 渲染模板
    template = env.get_template("tools/champion_comparisons.html")
    html_content = template.render(
        request=request,
        user=user,
        champion=champion,
        champion_id=champion_id,
        comparisons=comparisons,
        version=version
    )

    return HTMLResponse(content=html_content)


@router.get("/{comparison_id}", response_class=JSONResponse)
async def get_comparison_detail(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """获取对比详情"""
    user = require_login(request)
    if not user:
        return JSONResponse(content={"error": "请先登录"}, status_code=401)

    comparison = session.get(ChampionComparison, comparison_id)
    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    # 获取英雄信息
    champion1 = champion_service.get_champion_by_id(comparison.champion1_id)
    champion2 = champion_service.get_champion_by_id(comparison.champion2_id)
    version = champion_service.get_version()

    return JSONResponse(content={
        "champion1": {
            "id": champion1.id,
            "name": champion1.name,
            "title": champion1.title,
            "image": {"full": champion1.image.full}
        },
        "champion2": {
            "id": champion2.id,
            "name": champion2.name,
            "title": champion2.title,
            "image": {"full": champion2.image.full}
        },
        "ai_commentary": comparison.ai_commentary,
        "ai_tags": comparison.ai_tags.split(',') if comparison.ai_tags else [],
        "stats_comparison": comparison.stats_comparison,
        "version": version
    })


@router.delete("/{comparison_id}", response_class=JSONResponse)
async def delete_comparison(comparison_id: int, request: Request, session: Session = Depends(get_session)):
    """删除对比报告"""
    user = require_login(request)
    if not user:
        return JSONResponse(content={"error": "请先登录"}, status_code=401)

    comparison = session.get(ChampionComparison, comparison_id)
    if not comparison:
        return JSONResponse(content={"error": "对比报告不存在"}, status_code=404)

    session.delete(comparison)
    session.commit()

    return JSONResponse(content={"success": True})


