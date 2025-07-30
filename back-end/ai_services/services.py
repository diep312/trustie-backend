import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2] / 'ai-engine'))

from service.ocr_service import OCRService

def extract_text_from_image(image_path: str, lang: str = 'vie') -> str:
    return OCRService.extract_text(image_path, lang) 