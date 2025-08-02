from .pipelines.ocr_service import OCRService
from .pipelines.llms import LLMService
from .pipelines.tts_service import TTSService
from typing import Dict, Any

class AIServices:
    def __init__(self):
        """Initialize AI services with OCR, LLM, and TTS capabilities"""
        self.ocr_service = OCRService()
        self.llm_service = LLMService()
        self.tts_service = TTSService()
    
    def extract_text_from_image(self, image_path: str, lang: str = 'vie') -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            lang: Language code for OCR (default: 'vie' for Vietnamese)
            
        Returns:
            Extracted text string
        """
        return self.ocr_service.extract_text(image_path, lang)
    
    def analyze_scam_risk(self, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze text for scam risk using LLM
        
        Args:
            text: Text to analyze
            entities: Dictionary containing extracted entities (phones, urls, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        return self.llm_service.analyze_scam_risk(text, entities)
    
    def analyze_image_scam_risk(self, image_path: str, text: str = "", entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze image for scam risk using LLM with multimodal capabilities
        
        Args:
            image_path: Path to the image file
            text: Optional text extracted from OCR
            entities: Dictionary containing extracted entities (phones, urls, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        return self.llm_service.analyze_image_scam_risk(image_path, text, entities)
    
    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech using TTS service
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Dictionary containing file path and metadata
        """
        return self.tts_service.text_to_speech(text)
    
    def get_tts_models(self) -> Dict[str, Any]:
        """
        Get information about available TTS models
        
        Returns:
            Dictionary with model information
        """
        return self.tts_service.get_available_models()
    
    def analyze_text_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        General text analysis using LLM
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (general, sentiment, summary)
            
        Returns:
            Dictionary containing analysis results
        """
        return self.llm_service.analyze_text_content(text, analysis_type)
    
    def process_screenshot_analysis(self, image_path: str, lang: str = 'vie') -> Dict[str, Any]:
        """
        Complete screenshot processing pipeline with image analysis
        
        Args:
            image_path: Path to the screenshot image
            lang: Language for OCR processing
            
        Returns:
            Dictionary containing OCR text, entities, and LLM analysis
        """
        # Extract text using OCR
        ocr_text = self.extract_text_from_image(image_path, lang)
        
        # Extract entities (this would need to be implemented or imported)
        entities = self._extract_entities(ocr_text)
        
        # Analyze with LLM using both text and image
        llm_result = self.analyze_image_scam_risk(image_path, ocr_text, entities)
        
        return {
            "ocr_text": ocr_text,
            "entities": entities,
            "llm_analysis": llm_result
        }
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text (phone numbers, URLs, etc.)
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary containing extracted entities
        """
        import re
        
        # Extract phone numbers
        phones = re.findall(r'\+?\d[\d\- ]{7,}\d', text)
        
        # Extract URLs
        urls = re.findall(r'(https?://\S+)', text)
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        return {
            "phones": phones,
            "urls": urls,
            "emails": emails
        }

# Create a global instance for easy access
ai_services = AIServices()

# Convenience functions for backward compatibility
def extract_text_from_image(image_path: str, lang: str = 'vie') -> str:
    return ai_services.extract_text_from_image(image_path, lang)

def analyze_scam_risk(text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    return ai_services.analyze_scam_risk(text, entities)

def analyze_image_scam_risk(image_path: str, text: str = "", entities: Dict[str, Any] = None) -> Dict[str, Any]:
    return ai_services.analyze_image_scam_risk(image_path, text, entities)

def text_to_speech(text: str) -> Dict[str, Any]:
    return ai_services.text_to_speech(text)

def get_tts_models() -> Dict[str, Any]:
    return ai_services.get_tts_models()

def analyze_text_content(text: str, analysis_type: str = "general") -> Dict[str, Any]:
    return ai_services.analyze_text_content(text, analysis_type)