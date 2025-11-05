"""
录像路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Optional, List, Dict
from datetime import datetime
import os
import shutil

from database import get_session
from models import User, Replay
from services.replay_service import replay_service

router = APIRouter(prefix="/replays", tags=["replays"])

templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


def get_current_user(request: Request, session: Session) -> Optional[User]:
    """获取当前登录用户"""
    user_session = request.session.get('user')
    if not user_session:
        return None

    db_user = session.exec(
        select(User).where(
            User.provider == user_session['provider'],
            User.provider_user_id == user_session['provider_id']
        )
    ).first()

    return db_user


@router.get("/list", response_class=HTMLResponse)
def replay_list_page(
    request: Request,
    session: Session = Depends(get_session)
):
    """录像列表页面"""
    db_user = get_current_user(request, session)
    if not db_user:
        return HTMLResponse(content="<script>window.location.href='/login'</script>")

    replays = replay_service.get_user_replays(session, db_user.id)

    template = env.get_template("replays/list.html")
    return HTMLResponse(content=template.render(
        request=request,
        user=db_user,
        replays=replays
    ))


@router.get("/import", response_class=HTMLResponse)
def replay_import_page(
    request: Request,
    session: Session = Depends(get_session)
):
    """录像导入页面"""
    db_user = get_current_user(request, session)
    if not db_user:
        return HTMLResponse(content="<script>window.location.href='/login'</script>")

    template = env.get_template("replays/import.html")
    return HTMLResponse(content=template.render(
        request=request,
        user=db_user
    ))


@router.post("/scan")
def scan_folder(
    request: Request,
    folder_path: str = Form(...),
    session: Session = Depends(get_session)
):
    """扫描文件夹中的.rofl文件"""
    db_user = get_current_user(request, session)
    if not db_user:
        return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)

    path = Path(folder_path)

    if not path.exists():
        return JSONResponse(content={"success": False, "message": "文件夹不存在"})

    if not path.is_dir():
        return JSONResponse(content={"success": False, "message": "路径不是文件夹"})

    files: List[Dict] = []

    for file_path in path.glob("*.rofl"):
        stat = file_path.stat()
        files.append({
            "name": file_path.name,
            "size": stat.st_size,
            "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "title": "",
            "description": "",
            "status": "pending"
        })

    files.sort(key=lambda x: x["date"], reverse=True)

    return JSONResponse(content={
        "success": True,
        "files": files,
        "count": len(files)
    })


@router.post("/import")
def import_replay_action(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    original_path: str = Form(...),
    session: Session = Depends(get_session)
):
    """导入录像表单处理"""
    db_user = get_current_user(request, session)
    if not db_user:
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header or request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)
        return RedirectResponse(url="/login", status_code=303)

    replay = replay_service.import_replay(
        session=session,
        user_id=db_user.id,
        name=name,
        original_path=original_path,
        description=description
    )

    accept_header = request.headers.get("accept", "")
    is_ajax = "application/json" in accept_header or request.headers.get("x-requested-with") == "XMLHttpRequest"

    if not replay:
        if is_ajax:
            return JSONResponse(content={"success": False, "message": "文件不存在或导入失败"}, status_code=400)
        return RedirectResponse(url="/replays/import?error=文件不存在或导入失败", status_code=303)

    if is_ajax:
        return JSONResponse(content={"success": True, "message": "导入成功"})

    return RedirectResponse(url="/replays/list", status_code=303)


@router.post("/{replay_id}/update")
def update_replay_action(
    replay_id: int,
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """更新录像信息表单处理"""
    db_user = get_current_user(request, session)
    if not db_user:
        return RedirectResponse(url="/login", status_code=303)

    replay = replay_service.update_replay(
        session=session,
        replay_id=replay_id,
        user_id=db_user.id,
        name=name,
        description=description
    )

    if not replay:
        return RedirectResponse(url="/replays/list?error=录像不存在", status_code=303)

    return RedirectResponse(url="/replays/list", status_code=303)


@router.post("/{replay_id}/delete")
def delete_replay_action(
    replay_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """删除录像表单处理"""
    db_user = get_current_user(request, session)
    if not db_user:
        return RedirectResponse(url="/login", status_code=303)

    success = replay_service.delete_replay(
        session=session,
        replay_id=replay_id,
        user_id=db_user.id
    )

    if not success:
        return RedirectResponse(url="/replays/list?error=录像不存在", status_code=303)

    return RedirectResponse(url="/replays/list", status_code=303)


@router.get("/{replay_id}/download")
def download_replay(
    replay_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """下载录像文件"""
    db_user = get_current_user(request, session)
    if not db_user:
        return RedirectResponse(url="/login", status_code=303)

    replay = replay_service.get_replay_by_id(session, replay_id, db_user.id)

    if not replay:
        raise HTTPException(status_code=404, detail="录像不存在")

    stored_path = Path(replay.stored_path)

    if not stored_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=stored_path,
        filename=stored_path.name,
        media_type="application/octet-stream"
    )


@router.post("/{replay_id}/replace")
def replace_replay_to_lol(
    replay_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """自动替换录像到LOL客户端录像文件夹"""
    db_user = get_current_user(request, session)
    if not db_user:
        return JSONResponse(content={"success": False, "message": "未登录"}, status_code=401)

    replay = replay_service.get_replay_by_id(session, replay_id, db_user.id)

    if not replay:
        return JSONResponse(content={"success": False, "message": "录像不存在"}, status_code=404)

    stored_path = Path(replay.stored_path)

    if not stored_path.exists():
        return JSONResponse(content={"success": False, "message": "录像文件不存在"}, status_code=404)

    user_home = Path.home()
    lol_replays_dir = user_home / "Documents" / "League of Legends" / "Replays"

    if not lol_replays_dir.exists():
        return JSONResponse(content={
            "success": False,
            "message": "未找到LOL录像文件夹，请确保已下载过至少一次录像"
        }, status_code=400)

    replay_files = list(lol_replays_dir.glob("*.rofl"))

    if not replay_files:
        return JSONResponse(content={
            "success": False,
            "message": "LOL录像文件夹中没有录像文件，请先在客户端下载一局录像"
        }, status_code=400)

    replay_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_replay = replay_files[0]

    shutil.copy2(stored_path, latest_replay)

    return JSONResponse(content={
        "success": True,
        "message": f"已成功替换录像文件：{latest_replay.name}",
        "replaced_file": str(latest_replay)
    })
