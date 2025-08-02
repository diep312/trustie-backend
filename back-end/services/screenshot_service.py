import os
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.screenshot import Screenshot
from ..schemas import ScreenshotCreate
from ..ai_services.services import ai_services
import re
import logging
from werkzeug.utils import secure_filename 

logger = logging.getLogger(__name__)

class ScreenshotService:
    def __init__(self, db: Session, upload_dir: str = "./data/screenshot_uploads"):
        self.db = db
        self.upload_dir = os.path.abspath(upload_dir)

    def save_screenshot(self, file, user_id: int, description: Optional[str] = None) -> Screenshot:
        # Create user-specific upload directory
        user_dir = os.path.join(self.upload_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        # Secure and build filename
        base_filename = secure_filename(file.filename)
        file_root, file_ext = os.path.splitext(base_filename)
        file_path = os.path.join(user_dir, base_filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        new_filename = f"{file_root}_{timestamp}{file_ext}"
        file_path = os.path.join(user_dir, new_filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Create DB record
        screenshot = Screenshot(
            image_path=file_path,
            image_size=os.path.getsize(file_path),
            image_format=file_ext.lstrip('.'),
            description=description,
            is_processed=False,
            user_id=user_id,
            created_at=datetime.utcnow(),
            timestamp=datetime.utcnow()
        )
        self.db.add(screenshot)
        self.db.commit()
        self.db.refresh(screenshot)
        return screenshot


    def run_ocr(self, screenshot: Screenshot, lang: str = 'vie') -> str:
        text = ai_services.extract_text_from_image(screenshot.image_path, lang=lang)
        screenshot.ocr_text = text
        screenshot.is_processed = True
        return text

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using the AI services layer
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary containing extracted entities
        """
        # Use the AI services layer for entity extraction
        return ai_services._extract_entities(text)

    def analyze_with_llm(self, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze text for scam risk using the AI services layer
        
        Args:
            text: Text to analyze
            entities: Dictionary containing extracted entities
            
        Returns:
            Dictionary containing analysis results
        """
        return ai_services.analyze_scam_risk(text, entities)

    def analyze_image_with_llm(self, image_path: str, text: str = "", entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze image for scam risk using the AI services layer with multimodal capabilities
        
        Args:
            image_path: Path to the image file
            text: Optional text extracted from OCR
            entities: Dictionary containing extracted entities
            
        Returns:
            Dictionary containing analysis results
        """
        return ai_services.analyze_image_scam_risk(image_path, text, entities)

    def process_screenshot(self, file, user_id: int, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Process screenshot using the complete AI services pipeline with image analysis
        
        Args:
            file: Uploaded file
            user_id: User ID
            description: Optional description
            
        Returns:
            Dictionary containing processing results
        """
        screenshot = self.save_screenshot(file, user_id, description)
        
        # Use the complete AI services pipeline with image analysis
        analysis_result = ai_services.process_screenshot_analysis(screenshot.image_path)
        
        # Update screenshot with OCR text
        screenshot.ocr_text = analysis_result["ocr_text"]
        screenshot.is_processed = True
        self.db.commit()
        
        return {
            "screenshot_id": screenshot.id,
            "ocr_text": analysis_result["ocr_text"],
            "entities": analysis_result["entities"],
            "llm_analysis": analysis_result["llm_analysis"],
            "image_analyzed": analysis_result["llm_analysis"].get("image_analyzed", False)
        }