from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from sqlmodel import Session, select
from services.champion_service import champion_service
from services.rune_service import rune_service
from services.summoner_service import summoner_service
from services.item_service import item_service
from schemas.champion import ChampionModel
from schemas.user import UserInfo
from typing import Dict, List
from config import settings
from oauth_providers import oauth
from database import create_db_and_tables, get_session
from models import User, RunePage, TeamComposition, ChampionFavorite, HighlightVideo, ChampionTip, ItemBuild
from routes import summoner, champion, item, team_composition, highlight
from services.ffmpeg_service import ffmpeg_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动中...")

    # 创建数据库表
    create_db_and_tables()
    print("数据库表创建完成")

    # 加载英雄数据
    champion_service.load_champions()
    print(f"英雄数据加载完成,版本: {champion_service.get_version()}")

    # 加载符文数据
    rune_service.load_runes()
    print(f"符文数据加载完成,版本: {rune_service.get_version()}")

    # 加载召唤师技能数据
    summoner_service.load_summoner_spells()
    print(f"召唤师技能数据加载完成,版本: {summoner_service.get_version()}")

    # 加载装备数据
    item_service.load_items()
    print(f"装备数据加载完成,版本: {item_service.get_version()}")

    # 检测ffmpeg
    if ffmpeg_service.is_ffmpeg_installed():
        print(f"FFmpeg已安装: {ffmpeg_service.get_ffmpeg_version()}")
    else:
        print("FFmpeg未安装，高亮导入功能将不可用")

    yield
    print("应用关闭中...")


app = FastAPI(title="LOL助手", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# 注册路由
app.include_router(champion.router)
app.include_router(summoner.router)
app.include_router(item.router)
app.include_router(team_composition.router)
app.include_router(highlight.router)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"user": user}
    )





@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/auth/login/{provider}")
async def oauth_login(request: Request, provider: str):
    """OAuth登录跳转"""
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@app.get("/auth/callback/{provider}")
async def oauth_callback(request: Request, provider: str, session: Session = Depends(get_session)):
    """OAuth回调处理"""
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    provider_user_id = ''
    if provider == 'github':
        resp = await client.get('user', token=token)
        profile = resp.json()
        provider_user_id = str(profile.get('id', ''))
        user_info = UserInfo(
            provider='GitHub',
            provider_id=provider_user_id,
            name=profile.get('login') or '',
            email=profile.get('email') or '',
            avatar=profile.get('avatar_url') or '',
            raw_data=profile
        )
    elif provider == 'google':
        user_data = token.get('userinfo')
        provider_user_id = user_data.get('sub', '')
        user_info = UserInfo(
            provider='Google',
            provider_id=provider_user_id,
            name=user_data.get('name') or '',
            email=user_data.get('email') or '',
            avatar=user_data.get('picture') or '',
            raw_data=user_data
        )
    else:
        return RedirectResponse(url='/')

    # 保存或更新用户到数据库
    db_user = session.exec(
        select(User).where(
            User.provider == user_info.provider,
            User.provider_user_id == provider_user_id
        )
    ).first()

    if not db_user:
        # 创建新用户
        db_user = User(
            provider=user_info.provider,
            provider_user_id=provider_user_id,
            name=user_info.name,
            email=user_info.email,
            avatar=user_info.avatar
        )
        session.add(db_user)
    else:
        # 更新用户信息
        db_user.name = user_info.name
        db_user.email = user_info.email
        db_user.avatar = user_info.avatar

    session.commit()

    request.session['user'] = user_info.model_dump()
    return RedirectResponse(url='/')


@app.get("/auth/logout")
async def logout(request: Request):
    """退出登录"""
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@app.get("/runes", response_class=HTMLResponse)
async def runes_page(request: Request, edit: int = None, session: Session = Depends(get_session)):
    """符文配置页面"""
    user = request.session.get('user')
    rune_trees = [tree.model_dump() for tree in rune_service.get_all_trees().values()]

    edit_page = None
    if edit and user:
        # 查找用户
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            # 查找符文页
            rune_page = session.exec(
                select(RunePage).where(
                    RunePage.id == edit,
                    RunePage.user_id == db_user.id
                )
            ).first()

            if rune_page:
                # 转换为字典
                edit_page = {
                    'id': rune_page.id,
                    'name': rune_page.name,
                    'champion_id': rune_page.champion_id,
                    'primary_tree_id': rune_page.primary_tree_id,
                    'primary_keystone_id': rune_page.primary_keystone_id,
                    'primary_slot1_id': rune_page.primary_slot1_id,
                    'primary_slot2_id': rune_page.primary_slot2_id,
                    'primary_slot3_id': rune_page.primary_slot3_id,
                    'secondary_tree_id': rune_page.secondary_tree_id,
                    'secondary_slot1_id': rune_page.secondary_slot1_id,
                    'secondary_slot2_id': rune_page.secondary_slot2_id
                }

    return templates.TemplateResponse(
        request=request,
        name="runes.html",
        context={
            "user": user,
            "rune_trees": rune_trees,
            "version": rune_service.get_version(),
            "edit_page": edit_page
        }
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, session: Session = Depends(get_session)):
    """个人资料页面"""
    user = request.session.get('user')

    # 获取用户的符文页、收藏的英雄和配装方案
    rune_pages = []
    favorite_champions = []
    item_builds = []
    if user:
        # 查找或创建用户
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            # 获取用户的符文页
            rune_pages = session.exec(
                select(RunePage).where(RunePage.user_id == db_user.id)
            ).all()

            # 获取用户收藏的英雄
            favorites = session.exec(
                select(ChampionFavorite).where(ChampionFavorite.user_id == db_user.id)
            ).all()

            # 获取英雄详细信息
            from services.champion_service import champion_service
            for fav in favorites:
                champion = champion_service.get_champion_by_id(fav.champion_id)
                if champion:
                    favorite_champions.append({
                        'favorite_id': fav.id,
                        'champion': champion,
                        'created_at': fav.created_at
                    })

            # 获取用户的配装方案
            item_builds = session.exec(
                select(ItemBuild).where(ItemBuild.user_id == db_user.id).order_by(ItemBuild.updated_at.desc())
            ).all()

    ffmpeg_installed = ffmpeg_service.is_ffmpeg_installed()

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "rune_pages": rune_pages,
            "favorite_champions": favorite_champions,
            "item_builds": item_builds,
            "item_version": item_service.get_version(),
            "ffmpeg_installed": ffmpeg_installed
        }
    )


@app.post("/runes/save")
async def save_rune_page(request: Request, session: Session = Depends(get_session)):
    """保存符文页"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/auth/login/github', status_code=303)

    form_data = await request.form()

    # 查找用户
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if not db_user:
        return RedirectResponse(url='/auth/login/github', status_code=303)

    edit_id = form_data.get('edit_id')

    if edit_id:
        # 更新现有符文页
        rune_page = session.exec(
            select(RunePage).where(
                RunePage.id == int(edit_id),
                RunePage.user_id == db_user.id
            )
        ).first()

        if rune_page:
            rune_page.name = form_data.get('name')
            rune_page.champion_id = form_data.get('champion_id') or None
            rune_page.primary_tree_id = int(form_data.get('primary_tree_id'))
            rune_page.primary_keystone_id = int(form_data.get('primary_keystone_id'))
            rune_page.primary_slot1_id = int(form_data.get('primary_slot1_id'))
            rune_page.primary_slot2_id = int(form_data.get('primary_slot2_id'))
            rune_page.primary_slot3_id = int(form_data.get('primary_slot3_id'))
            rune_page.secondary_tree_id = int(form_data.get('secondary_tree_id'))
            rune_page.secondary_slot1_id = int(form_data.get('secondary_slot1_id'))
            rune_page.secondary_slot2_id = int(form_data.get('secondary_slot2_id'))
            rune_page.updated_at = datetime.now()
    else:
        # 创建新符文页
        rune_page = RunePage(
            user_id=db_user.id,
            name=form_data.get('name'),
            champion_id=form_data.get('champion_id') or None,
            primary_tree_id=int(form_data.get('primary_tree_id')),
            primary_keystone_id=int(form_data.get('primary_keystone_id')),
            primary_slot1_id=int(form_data.get('primary_slot1_id')),
            primary_slot2_id=int(form_data.get('primary_slot2_id')),
            primary_slot3_id=int(form_data.get('primary_slot3_id')),
            secondary_tree_id=int(form_data.get('secondary_tree_id')),
            secondary_slot1_id=int(form_data.get('secondary_slot1_id')),
            secondary_slot2_id=int(form_data.get('secondary_slot2_id'))
        )
        session.add(rune_page)

    session.commit()
    return RedirectResponse(url='/profile', status_code=303)


@app.post("/profile/rune-pages/{page_id}/delete")
async def delete_rune_page(page_id: int, request: Request, session: Session = Depends(get_session)):
    """删除符文页"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/profile', status_code=303)

    # 查找用户
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()

    if db_user:
        # 查找并删除符文页
        rune_page = session.exec(
            select(RunePage).where(
                RunePage.id == page_id,
                RunePage.user_id == db_user.id
            )
        ).first()

        if rune_page:
            session.delete(rune_page)
            session.commit()

    return RedirectResponse(url='/profile', status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

