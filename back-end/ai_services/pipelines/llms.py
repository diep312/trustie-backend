from typing import Dict, Any, Optional
from .llmsbase import LLMProvider
from .geminiimpl import GeminiService
from .openaiimpl import OpenAIService

class LLMService:
    def __init__(self, provider: LLMProvider = LLMProvider.OPENAI, api_key: Optional[str] = None):
        """
        Initialize LLM service with specified provider
        
        Args:
            provider: LLM provider to use (GEMINI or OPENAI)
            api_key: Optional API key for the provider
        """
        self.provider = provider
        
        if provider == LLMProvider.GEMINI:
            self.impl = GeminiService(api_key)
        elif provider == LLMProvider.OPENAI:
            self.impl = OpenAIService(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def analyze_image_scam_risk(self, image_path: str, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze image for scam risk using the configured provider
        """
        return self.impl.analyze_image_scam_risk(image_path, text, entities)
    
    def analyze_text_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze text content using the configured provider
        """
        return self.impl.analyze_text_content(text, analysis_type)
    
    # Add other methods as needed, delegating to the implementation