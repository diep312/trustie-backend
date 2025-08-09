import os
import base64
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"

class LLMServiceBase(ABC):
    def __init__(self, api_key: Optional[str] = None, api_key_env: Optional[str] = None):
        """
        Base class for any LLM provider.
        Args:
            api_key: Direct API key string.
            api_key_env: Environment variable name containing the key.
        """
        load_dotenv(dotenv_path=Path(__file__).parent / ".env")

        if api_key:
            self.api_key = api_key
        elif api_key_env:
            self.api_key = os.getenv(api_key_env)
        else:
            raise ValueError("Must provide either `api_key` or `api_key_env`.")

        if not self.api_key:
            raise Exception(f"API key not found (env var: {api_key_env})")

    # --- Common utilities ---
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image to base64: {str(e)}")
            raise
    
    def _get_mime_type(self, image_path: str) -> str:
        """
        Get MIME type based on file extension
        
        Args:
            image_path: Path to the image file
            
        Returns:
            MIME type string
        """
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'image/jpeg')

    # --- Abstract methods ---
    @abstractmethod
    def analyze_image_scam_risk(self, image_path: str, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze_text_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        pass

    @abstractmethod
    def _build_image_analysis_prompt(self, text: str, entities: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _build_scam_analysis_prompt(self, text: str, entities: Dict[str, Any]) -> str:
        pass