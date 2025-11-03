"""
FFmpeg服务
"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional


class FFmpegService:
    """FFmpeg服务类"""
    
    @staticmethod
    def is_ffmpeg_installed() -> bool:
        """检测ffmpeg是否已安装"""
        return shutil.which("ffmpeg") is not None
    
    @staticmethod
    def get_ffmpeg_version() -> Optional[str]:
        """获取ffmpeg版本"""
        if not FFmpegService.is_ffmpeg_installed():
            return None
        
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            return first_line
        
        return None
    
    @staticmethod
    def convert_webm_to_mp4(input_path: Path, output_path: Path) -> bool:
        """将webm格式转换为mp4格式"""
        if not FFmpegService.is_ffmpeg_installed():
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            [
                "ffmpeg",
                "-i", str(input_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-strict", "experimental",
                "-y",
                str(output_path)
            ],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    @staticmethod
    def get_video_duration(video_path: Path) -> Optional[float]:
        """获取视频时长(秒)"""
        if not FFmpegService.is_ffmpeg_installed():
            return None
        
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        
        return None


ffmpeg_service = FFmpegService()

