from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from services.champion_service import champion_service
from services.rune_service import rune_service
from models.champion import ChampionModel
from models.user import UserInfo
from typing import Dict
from config import settings
from oauth_providers import oauth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动中...")

    # 加载英雄数据
    champion_service.load_champions()
    print(f"英雄数据加载完成,版本: {champion_service.get_version()}")

    # 加载符文数据
    rune_service.load_runes()
    print(f"符文数据加载完成,版本: {rune_service.get_version()}")

    yield
    print("应用关闭中...")


app = FastAPI(title="LOL助手", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

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


@app.get("/champions", response_class=HTMLResponse)
async def champions_list(request: Request):
    """英雄列表页面"""
    champions = list(champion_service.get_all_champions().values())
    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "champions": champions,
            "selected_champion": None
        }
    )


@app.get("/champions/{champion_id}", response_class=HTMLResponse)
async def champion_detail(request: Request, champion_id: str):
    """英雄详情页面"""
    champions = list(champion_service.get_all_champions().values())
    selected_champion = champion_service.get_champion_by_id(champion_id)

    if not selected_champion:
        return templates.TemplateResponse(
            request=request,
            name="champions.html",
            context={
                "champions": champions,
                "selected_champion": None,
                "error": f"未找到英雄: {champion_id}"
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="champions.html",
        context={
            "champions": champions,
            "selected_champion": selected_champion
        }
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
async def oauth_callback(request: Request, provider: str):
    """OAuth回调处理"""
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    if provider == 'github':
        resp = await client.get('user', token=token)
        profile = resp.json()
        user_info = UserInfo(
            provider='GitHub',
            name=profile.get('login') or '',
            email=profile.get('email') or '',
            avatar=profile.get('avatar_url') or '',
            raw_data=profile
        )
    elif provider == 'google':
        user_data = token.get('userinfo')
        user_info = UserInfo(
            provider='Google',
            name=user_data.get('name') or '',
            email=user_data.get('email') or '',
            avatar=user_data.get('picture') or '',
            raw_data=user_data
        )
    else:
        return RedirectResponse(url='/')

    request.session['user'] = user_info.model_dump()
    return RedirectResponse(url='/')


@app.get("/auth/logout")
async def logout(request: Request):
    """退出登录"""
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

