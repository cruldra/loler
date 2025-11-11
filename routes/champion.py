"""
英雄相关路由
"""
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from services.champion_service import champion_service
from services.ocr_service import ocr_service
from database import get_session
from models import User, ChampionFavorite, ChampionTip, ChampionVideo, ChampionSkill
from schemas import ChampionTipCreate, ChampionTipUpdate, ChampionTipResponse, ChampionVideoCreate, ChampionVideoUpdate, ChampionVideoResponse, ChampionSkillCreate, ChampionSkillUpdate, ChampionSkillResponse
from datetime import datetime
from pathlib import Path
import shutil

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

    # 检查用户是否已收藏该英雄，并获取技巧列表和视频列表
    is_favorited = False
    champion_tips = []
    champion_videos = []
    champion_skills = {}
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

            # 获取该用户的该英雄的技巧列表
            tips = session.exec(
                select(ChampionTip).where(
                    ChampionTip.user_id == db_user.id,
                    ChampionTip.champion_id == champion_id
                ).order_by(ChampionTip.sort_order, ChampionTip.created_at)
            ).all()
            champion_tips = list(tips)

            # 获取该用户的该英雄的视频列表
            videos = session.exec(
                select(ChampionVideo).where(
                    ChampionVideo.user_id == db_user.id,
                    ChampionVideo.champion_id == champion_id
                ).order_by(ChampionVideo.sort_order, ChampionVideo.created_at)
            ).all()
            champion_videos = list(videos)

            # 获取该用户的该英雄的技能详情
            skills = session.exec(
                select(ChampionSkill).where(
                    ChampionSkill.user_id == db_user.id,
                    ChampionSkill.champion_id == champion_id
                )
            ).all()
            # 转换为字典，以skill_type为key
            champion_skills = {skill.skill_type: skill for skill in skills}

    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "user": user,
            "champions": champions,
            "selected_champion": selected_champion,
            "is_favorited": is_favorited,
            "champion_tips": champion_tips,
            "champion_videos": champion_videos,
            "champion_skills": champion_skills
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


@router.post("/{champion_id}/tips")
async def create_tip(
    request: Request,
    champion_id: str,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(default="通用"),
    session: Session = Depends(get_session)
):
    """创建英雄技巧"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    new_tip = ChampionTip(
        user_id=db_user.id,
        champion_id=champion_id,
        title=title,
        content=content,
        category=category
    )
    session.add(new_tip)
    session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


@router.post("/{champion_id}/tips/{tip_id}")
async def update_tip(
    request: Request,
    champion_id: str,
    tip_id: int,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    session: Session = Depends(get_session)
):
    """更新英雄技巧"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    tip = session.exec(
        select(ChampionTip).where(
            ChampionTip.id == tip_id,
            ChampionTip.user_id == db_user.id
        )
    ).first()

    if tip:
        tip.title = title
        tip.content = content
        tip.category = category
        tip.updated_at = datetime.now()
        session.add(tip)
        session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


@router.post("/{champion_id}/tips/{tip_id}/delete")
async def delete_tip(
    request: Request,
    champion_id: str,
    tip_id: int,
    session: Session = Depends(get_session)
):
    """删除英雄技巧"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    tip = session.exec(
        select(ChampionTip).where(
            ChampionTip.id == tip_id,
            ChampionTip.user_id == db_user.id
        )
    ).first()

    if tip:
        session.delete(tip)
        session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


@router.post("/{champion_id}/videos/create")
async def create_video(
    request: Request,
    champion_id: str,
    title: str = Form(...),
    url: str = Form(...),
    description: str = Form(None),
    platform: str = Form("bilibili"),
    session: Session = Depends(get_session)
):
    """创建英雄教学视频"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    video = ChampionVideo(
        user_id=db_user.id,
        champion_id=champion_id,
        title=title,
        url=url,
        description=description,
        platform=platform
    )
    session.add(video)
    session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


@router.post("/{champion_id}/videos/{video_id}/update")
async def update_video(
    request: Request,
    champion_id: str,
    video_id: int,
    title: str = Form(...),
    url: str = Form(...),
    description: str = Form(None),
    platform: str = Form("bilibili"),
    session: Session = Depends(get_session)
):
    """更新英雄教学视频"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    video = session.exec(
        select(ChampionVideo).where(
            ChampionVideo.id == video_id,
            ChampionVideo.user_id == db_user.id
        )
    ).first()

    if video:
        video.title = title
        video.url = url
        video.description = description
        video.platform = platform
        video.updated_at = datetime.now()
        session.add(video)
        session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


@router.post("/{champion_id}/videos/{video_id}/delete")
async def delete_video(
    request: Request,
    champion_id: str,
    video_id: int,
    session: Session = Depends(get_session)
):
    """删除英雄教学视频"""
    user = request.session.get('user')

    if not user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)

    video = session.exec(
        select(ChampionVideo).where(
            ChampionVideo.id == video_id,
            ChampionVideo.user_id == db_user.id
        )
    ).first()

    if video:
        session.delete(video)
        session.commit()

    return RedirectResponse(url=f"/champions/{champion_id}", status_code=303)


def get_current_user(request: Request, session: Session) -> User:
    """获取当前登录用户"""
    user = request.session.get('user')
    if not user:
        return None

    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    return db_user


@router.post("/{champion_id}/skills/upload")
async def upload_skill_image(
    request: Request,
    champion_id: str,
    skill_type: str = Form(...),
    image: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """上传技能图片并进行OCR识别"""
    db_user = get_current_user(request, session)
    if not db_user:
        return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)

    # 创建上传目录
    upload_dir = Path("static/uploads/skills")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 保存图片
    file_ext = Path(image.filename).suffix
    file_name = f"{champion_id}_{skill_type}_{db_user.id}{file_ext}"
    file_path = upload_dir / file_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # OCR识别
    ocr_text = ocr_service.recognize_text(str(file_path))

    # 查找或创建技能详情记录
    skill = session.exec(
        select(ChampionSkill).where(
            ChampionSkill.user_id == db_user.id,
            ChampionSkill.champion_id == champion_id,
            ChampionSkill.skill_type == skill_type
        )
    ).first()

    if skill:
        # 更新现有记录
        skill.image_path = f"/static/uploads/skills/{file_name}"
        skill.ocr_description = ocr_text
        skill.updated_at = datetime.now()
    else:
        # 创建新记录
        skill = ChampionSkill(
            user_id=db_user.id,
            champion_id=champion_id,
            skill_type=skill_type,
            image_path=f"/static/uploads/skills/{file_name}",
            ocr_description=ocr_text
        )
        session.add(skill)

    session.commit()
    session.refresh(skill)

    return JSONResponse(content={
        "success": True,
        "message": "图片上传成功",
        "data": {
            "id": skill.id,
            "image_path": skill.image_path,
            "ocr_description": skill.ocr_description
        }
    })


@router.post("/{champion_id}/skills/{skill_type}/notes")
async def update_skill_notes(
    request: Request,
    champion_id: str,
    skill_type: str,
    personal_notes: str = Form(...),
    session: Session = Depends(get_session)
):
    """更新技能个人见解"""
    db_user = get_current_user(request, session)
    if not db_user:
        return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)

    # 查找或创建技能详情记录
    skill = session.exec(
        select(ChampionSkill).where(
            ChampionSkill.user_id == db_user.id,
            ChampionSkill.champion_id == champion_id,
            ChampionSkill.skill_type == skill_type
        )
    ).first()

    if skill:
        # 更新现有记录
        skill.personal_notes = personal_notes
        skill.updated_at = datetime.now()
    else:
        # 创建新记录
        skill = ChampionSkill(
            user_id=db_user.id,
            champion_id=champion_id,
            skill_type=skill_type,
            personal_notes=personal_notes
        )
        session.add(skill)

    session.commit()
    session.refresh(skill)

    return JSONResponse(content={
        "success": True,
        "message": "个人见解保存成功",
        "data": {
            "id": skill.id,
            "personal_notes": skill.personal_notes
        }
    })


@router.get("/{champion_id}/skills/{skill_type}")
async def get_skill_detail(
    request: Request,
    champion_id: str,
    skill_type: str,
    session: Session = Depends(get_session)
):
    """获取技能详情"""
    db_user = get_current_user(request, session)
    if not db_user:
        return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)

    skill = session.exec(
        select(ChampionSkill).where(
            ChampionSkill.user_id == db_user.id,
            ChampionSkill.champion_id == champion_id,
            ChampionSkill.skill_type == skill_type
        )
    ).first()

    if not skill:
        return JSONResponse(content={"success": False, "message": "未找到技能详情"}, status_code=404)

    return JSONResponse(content={
        "success": True,
        "data": {
            "id": skill.id,
            "skill_type": skill.skill_type,
            "image_path": skill.image_path,
            "ocr_description": skill.ocr_description,
            "personal_notes": skill.personal_notes
        }
    })

