"""
高亮视频路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from sqlmodel import Session
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from database import get_session
from models import User, HighlightVideo
from schemas.highlight import (
    HighlightVideoResponse,
    HighlightImportResponse
)
from services.highlight_service import highlight_service
from services.ffmpeg_service import ffmpeg_service
from sqlmodel import select

router = APIRouter(prefix="/highlights", tags=["highlights"])

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    """获取当前登录用户"""
    user_session = request.session.get('user')
    if not user_session:
        raise HTTPException(status_code=401, detail="未登录")
    
    db_user = session.exec(
        select(User).where(
            User.provider == user_session['provider'],
            User.provider_user_id == user_session['provider_id']
        )
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return db_user


@router.get("/page", response_class=HTMLResponse)
async def highlight_page(
    request: Request,
    session: Session = Depends(get_session)
):
    """高亮视频导入页面"""
    user_session = request.session.get('user')
    
    if not user_session:
        return HTMLResponse(content="<script>window.location.href='/login';</script>")
    
    db_user = session.exec(
        select(User).where(
            User.provider == user_session['provider'],
            User.provider_user_id == user_session['provider_id']
        )
    ).first()
    
    if not db_user:
        return HTMLResponse(content="<script>window.location.href='/login';</script>")
    
    videos = highlight_service.get_user_videos(session, db_user.id)
    ffmpeg_installed = ffmpeg_service.is_ffmpeg_installed()
    highlights_dir = highlight_service.get_highlights_directory()
    
    template = templates_env.get_template("highlights.html")
    html_content = template.render(
        user=user_session,
        videos=videos,
        ffmpeg_installed=ffmpeg_installed,
        highlights_dir=str(highlights_dir)
    )
    
    return HTMLResponse(content=html_content)


@router.get("/list", response_model=List[HighlightVideoResponse])
async def list_videos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取用户的高亮视频列表"""
    videos = highlight_service.get_user_videos(session, current_user.id)
    return videos


@router.post("/import", response_model=HighlightImportResponse)
async def import_highlights(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """导入高亮视频"""
    
    if not ffmpeg_service.is_ffmpeg_installed():
        raise HTTPException(status_code=400, detail="FFmpeg未安装")
    
    video_files = highlight_service.scan_highlight_videos()
    
    if not video_files:
        return HighlightImportResponse(
            success=True,
            imported_count=0,
            skipped_count=0,
            message="未找到高亮视频文件"
        )
    
    imported_count = 0
    skipped_count = 0
    
    for video_file in video_files:
        result = highlight_service.import_highlight_video(
            session,
            current_user.id,
            video_file
        )
        
        if result:
            imported_count += 1
        else:
            skipped_count += 1
    
    return HighlightImportResponse(
        success=True,
        imported_count=imported_count,
        skipped_count=skipped_count,
        message=f"成功导入 {imported_count} 个视频，跳过 {skipped_count} 个已存在的视频"
    )


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """删除视频"""
    success = highlight_service.delete_video(session, video_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    return {"success": True, "message": "删除成功"}


@router.get("/video/{video_id}")
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取视频文件"""
    video = session.exec(
        select(HighlightVideo).where(
            HighlightVideo.id == video_id,
            HighlightVideo.user_id == current_user.id,
            HighlightVideo.is_deleted == False
        )
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    video_path = Path(video.converted_path)

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"{video.name}.mp4"
    )

