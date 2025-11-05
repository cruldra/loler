"""
录像服务类
"""
from pathlib import Path
from typing import List, Optional
from sqlmodel import Session, select
from models.replay import Replay
from datetime import datetime
import shutil


class ReplayService:
    """录像服务类"""
    
    @staticmethod
    def get_replays_directory() -> Path:
        """获取录像存储目录"""
        replays_dir = Path(__file__).parent.parent / "data" / "replays"
        replays_dir.mkdir(parents=True, exist_ok=True)
        return replays_dir
    
    @staticmethod
    def get_user_replays(session: Session, user_id: int) -> List[Replay]:
        """获取用户的所有录像"""
        statement = select(Replay).where(Replay.user_id == user_id).order_by(Replay.created_at.desc())
        replays = session.exec(statement).all()
        return list(replays)
    
    @staticmethod
    def get_replay_by_id(session: Session, replay_id: int, user_id: int) -> Optional[Replay]:
        """根据ID获取录像"""
        statement = select(Replay).where(
            Replay.id == replay_id,
            Replay.user_id == user_id
        )
        return session.exec(statement).first()
    
    @staticmethod
    def import_replay(
        session: Session,
        user_id: int,
        name: str,
        original_path: str,
        description: Optional[str] = None
    ) -> Optional[Replay]:
        """导入录像文件"""
        source_file = Path(original_path)
        
        if not source_file.exists():
            return None
        
        replays_dir = ReplayService.get_replays_directory()
        stored_file = replays_dir / source_file.name
        
        shutil.copy2(source_file, stored_file)
        
        file_size = stored_file.stat().st_size
        
        replay = Replay(
            user_id=user_id,
            name=name,
            description=description or "",
            original_path=str(source_file),
            stored_path=str(stored_file),
            file_size=file_size
        )
        
        session.add(replay)
        session.commit()
        session.refresh(replay)
        
        return replay
    
    @staticmethod
    def update_replay(
        session: Session,
        replay_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Replay]:
        """更新录像信息"""
        replay = ReplayService.get_replay_by_id(session, replay_id, user_id)
        
        if not replay:
            return None
        
        if name is not None:
            replay.name = name
        if description is not None:
            replay.description = description
        
        replay.updated_at = datetime.now()
        
        session.add(replay)
        session.commit()
        session.refresh(replay)
        
        return replay
    
    @staticmethod
    def delete_replay(session: Session, replay_id: int, user_id: int) -> bool:
        """删除录像"""
        replay = ReplayService.get_replay_by_id(session, replay_id, user_id)
        
        if not replay:
            return False
        
        stored_path = Path(replay.stored_path)
        if stored_path.exists():
            stored_path.unlink()
        
        session.delete(replay)
        session.commit()
        
        return True


replay_service = ReplayService()

