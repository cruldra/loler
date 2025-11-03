"""
高亮视频服务
"""
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from models.highlight_video import HighlightVideo
from services.ffmpeg_service import ffmpeg_service


class HighlightService:
    """高亮视频服务类"""
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """计算文件哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def is_video_imported(session: Session, file_hash: str) -> bool:
        """检查视频是否已导入"""
        video = session.exec(
            select(HighlightVideo).where(HighlightVideo.file_hash == file_hash)
        ).first()
        return video is not None
    
    @staticmethod
    def get_highlights_directory() -> Path:
        """获取英雄联盟高亮目录"""
        user_home = Path.home()
        highlights_dir = user_home / "Documents" / "League of Legends" / "Highlights"
        return highlights_dir
    
    @staticmethod
    def get_converted_videos_directory() -> Path:
        """获取转换后视频存储目录"""
        base_dir = Path(__file__).resolve().parent.parent
        converted_dir = base_dir / "data" / "highlights"
        converted_dir.mkdir(parents=True, exist_ok=True)
        return converted_dir
    
    @staticmethod
    def scan_highlight_videos() -> List[Path]:
        """扫描高亮视频文件"""
        highlights_dir = HighlightService.get_highlights_directory()
        
        if not highlights_dir.exists():
            return []
        
        webm_files = list(highlights_dir.glob("*.webm"))
        return webm_files
    
    @staticmethod
    def import_highlight_video(
        session: Session,
        user_id: int,
        source_file: Path
    ) -> Optional[HighlightVideo]:
        """导入单个高亮视频"""
        
        file_hash = HighlightService.calculate_file_hash(source_file)
        
        if HighlightService.is_video_imported(session, file_hash):
            return None
        
        converted_dir = HighlightService.get_converted_videos_directory()
        output_file = converted_dir / f"{source_file.stem}.mp4"
        
        if not ffmpeg_service.convert_webm_to_mp4(source_file, output_file):
            return None
        
        duration = ffmpeg_service.get_video_duration(output_file)
        
        video = HighlightVideo(
            user_id=user_id,
            name=source_file.stem,
            original_path=str(source_file),
            converted_path=str(output_file),
            file_hash=file_hash,
            file_size=source_file.stat().st_size,
            duration=duration
        )
        
        session.add(video)
        session.commit()
        session.refresh(video)
        
        return video
    
    @staticmethod
    def get_user_videos(session: Session, user_id: int) -> List[HighlightVideo]:
        """获取用户的所有高亮视频(不包括已删除的)"""
        videos = session.exec(
            select(HighlightVideo)
            .where(
                HighlightVideo.user_id == user_id,
                HighlightVideo.is_deleted == False
            )
            .order_by(HighlightVideo.created_at.desc())
        ).all()
        return list(videos)
    
    @staticmethod
    def delete_video(session: Session, video_id: int, user_id: int) -> bool:
        """逻辑删除视频(保留hash记录以防止重复导入)"""
        video = session.exec(
            select(HighlightVideo).where(
                HighlightVideo.id == video_id,
                HighlightVideo.user_id == user_id,
                HighlightVideo.is_deleted == False
            )
        ).first()

        if not video:
            return False

        converted_path = Path(video.converted_path)
        if converted_path.exists():
            converted_path.unlink()

        video.is_deleted = True
        video.deleted_at = datetime.now()
        session.add(video)
        session.commit()

        return True


highlight_service = HighlightService()

