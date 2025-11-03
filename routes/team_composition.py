"""
阵容配置相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from services.champion_service import champion_service
from database import get_session
from models import User, TeamComposition

router = APIRouter(prefix="/team-composition", tags=["team_composition"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def team_composition_page(request: Request, edit: int = None, session: Session = Depends(get_session)):
    """阵容配置页面"""
    user = request.session.get('user')
    champions = champion_service.get_all_champions()

    edit_composition = None

    if user and edit:
        db_user = session.exec(
            select(User).where(
                User.provider == user['provider'],
                User.provider_user_id == user['provider_id']
            )
        ).first()

        if db_user:
            edit_composition = session.exec(
                select(TeamComposition).where(
                    TeamComposition.id == edit,
                    TeamComposition.user_id == db_user.id
                )
            ).first()

    return templates.TemplateResponse(
        request=request,
        name="team_composition.html",
        context={
            "user": user,
            "champions": champions,
            "edit_composition": edit_composition
        }
    )


@router.post("/save")
async def save_team_composition(request: Request, session: Session = Depends(get_session)):
    """保存阵容配置"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    form_data = await request.form()
    
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()
    
    if not db_user:
        return RedirectResponse(url='/login', status_code=303)
    
    composition_id = form_data.get('composition_id')
    
    if composition_id:
        composition = session.exec(
            select(TeamComposition).where(
                TeamComposition.id == int(composition_id),
                TeamComposition.user_id == db_user.id
            )
        ).first()
        
        if composition:
            composition.name = form_data.get('name')
            composition.description = form_data.get('description') or None
            
            for team in [1, 2]:
                for player in range(1, 6):
                    prefix = f'team{team}_player{player}'
                    setattr(composition, f'{prefix}_champion', form_data.get(f'{prefix}_champion') or None)
                    setattr(composition, f'{prefix}_role', form_data.get(f'{prefix}_role') or None)
            
            composition.updated_at = datetime.now()
    else:
        composition_data = {
            'user_id': db_user.id,
            'name': form_data.get('name'),
            'description': form_data.get('description') or None
        }
        
        for team in [1, 2]:
            for player in range(1, 6):
                prefix = f'team{team}_player{player}'
                composition_data[f'{prefix}_champion'] = form_data.get(f'{prefix}_champion') or None
                composition_data[f'{prefix}_role'] = form_data.get(f'{prefix}_role') or None
        
        composition = TeamComposition(**composition_data)
        session.add(composition)
    
    session.commit()
    return RedirectResponse(url='/team-composition', status_code=303)


@router.post("/{composition_id}/delete")
async def delete_team_composition(composition_id: int, request: Request, session: Session = Depends(get_session)):
    """删除阵容配置"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/team-composition', status_code=303)
    
    db_user = session.exec(
        select(User).where(
            User.provider == user['provider'],
            User.provider_user_id == user['provider_id']
        )
    ).first()
    
    if db_user:
        composition = session.exec(
            select(TeamComposition).where(
                TeamComposition.id == composition_id,
                TeamComposition.user_id == db_user.id
            )
        ).first()
        
        if composition:
            session.delete(composition)
            session.commit()
    
    return RedirectResponse(url='/team-composition', status_code=303)

