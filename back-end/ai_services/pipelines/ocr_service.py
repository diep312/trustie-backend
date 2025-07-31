import pytesseract
from PIL import Image
from typing import Optional
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

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