from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from services.champion_service import champion_service
from models.champion import ChampionModel
from typing import Dict


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动中...")
    champion_service.load_champions()
    print(f"英雄数据加载完成,版本: {champion_service.get_version()}")
    yield
    print("应用关闭中...")


app = FastAPI(title="LOL助手", lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="base.html"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

