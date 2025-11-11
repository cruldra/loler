"""
OCR服务 - 使用PaddleOCR识别图片中的文字
"""
from pathlib import Path
from typing import Optional


class OCRService:
    """OCR服务类"""
    
    def __init__(self):
        """初始化OCR服务"""
        self._ocr = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保OCR已初始化"""
        if not self._initialized:
            from paddleocr import PaddleOCR
            # 使用中文模型
            self._ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            self._initialized = True
    
    def recognize_text(self, image_path: str) -> Optional[str]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别出的文字，如果失败返回None
        """
        image_file = Path(image_path)
        if not image_file.exists():
            return None
        
        self._ensure_initialized()

        result = self._ocr.ocr(str(image_file))
        
        if not result or not result[0]:
            return None
        
        # 提取所有识别的文字
        text_lines = []
        for line in result[0]:
            if line and len(line) >= 2:
                text = line[1][0]  # line[1][0]是识别的文字，line[1][1]是置信度
                text_lines.append(text)
        
        # 合并所有文字行
        return '\n'.join(text_lines) if text_lines else None


# 创建全局服务实例
ocr_service = OCRService()

