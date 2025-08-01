import pytesseract
from PIL import Image
from typing import Optional
import platform


def configure_tesseract_path():
    system = platform.system()
    
    if system == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    elif system == "Linux":
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    else:
        raise EnvironmentError(f"Unsupported OS: {system}")

configure_tesseract_path()

class OCRService:
    @staticmethod
    def extract_text(image_path: str, lang: Optional[str] = 'vie') -> str:
        """
        Extract text from an image file using pytesseract.
        :param image_path: Path to the image file
        :param lang: Language for OCR (default: 'eng')
        :return: Extracted text
        """
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text 