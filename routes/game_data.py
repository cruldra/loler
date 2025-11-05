"""
游戏资料路由
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json

router = APIRouter(prefix="/game-data", tags=["game-data"])

templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))

data_dir = Path(__file__).parent.parent / "data"


@router.get("/respawn-timer", response_class=HTMLResponse)
def respawn_timer_page():
    """复活时间表页面"""
    resurrection_file = data_dir / "resurrection_time.json"
    
    with open(resurrection_file, 'r', encoding='utf-8') as f:
        respawn_data = json.load(f)
    
    times = [item["复活时间"] for item in respawn_data]
    max_time = max(times)
    min_time = min(times)
    
    template = env.get_template("game_data/respawn_timer.html")
    return template.render(
        respawn_data=respawn_data,
        max_level=len(respawn_data),
        max_time=max_time,
        min_time=min_time
    )

