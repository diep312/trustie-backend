# openaiimpl.py
from openai import OpenAI
from typing import Dict, Any, Optional
import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from .llmsbase import LLMServiceBase
import json

logger = logging.getLogger(__name__)

class OpenAIService(LLMServiceBase):
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI LLM service with the new SDK
        
        Args:
            api_key: Optional API key, will load from environment if not provided
        """
        super().__init__(api_key=api_key, api_key_env="OPENAI_API_KEY")
        self.base_model = "gpt-4.1-mini"
        self.client = OpenAI(api_key=self.api_key)
    
    def analyze_image_scam_risk(self, image_path: str, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze image for scam or fraud risk using OpenAI's multimodal capabilities
        
        Args:
            image_path: Path to the image file
            text: Text extracted from screenshot
            entities: Dictionary containing extracted entities (phones, urls, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Encode image to base64
            image_data = self._encode_image_to_base64(image_path)
            
            # Build prompt for image analysis
            prompt = self._build_image_analysis_prompt(text, entities)
            
            response = self.client.chat.completions.create(
                model=self.base_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{self._get_mime_type(image_path)};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", analysis, re.DOTALL)
            json_str = json_match.group(1) if json_match else analysis.strip()
            json_response = json.loads(json_str)

            return {
                "analysis": json_response["ANALYSIS"],
                "recommendation": json_response["RECOMMENDATIONS"],
                "risk_level": json_response["RISK_LEVEL"],
                "confidence": int(json_response["CONFIDENCE"]),
                "model_used": self.base_model,
                "image_analyzed": True
            }
                
        except Exception as e:
            logger.error(f"Error in image scam risk analysis: {str(e)}")
            return {"error": str(e)}
    
    def analyze_text_content(self, text: str, analysis_type: str = "conversation") -> Dict[str, Any]:
        """
        General text analysis method
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        prompts = self._build_scam_analysis_prompt(text)
        
        
        try:
            response = self.client.chat.completions.create(
                model=self.base_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", analysis, re.DOTALL)
            json_str = json_match.group(1) if json_match else analysis.strip()
            json_response = json.loads(json_str)

            return {
                "analysis": json_response["ANALYSIS"],
                "recommendation": json_response["RECOMMENDATIONS"],
                "risk_level": json_response["RISK_LEVEL"],
                "confidence": int(json_response["CONFIDENCE"]),
                "model_used": self.base_model,
                "image_analyzed": True
            }
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            return {"error": str(e)}
    
    def _build_image_analysis_prompt(self, text: str, entities: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt for image-based scam analysis
        
        Args:
            text: Extracted text from OCR (if available)
            entities: Extracted entities
            
        Returns:
            Formatted prompt string
        """
        phones = entities.get('phones', [])
        urls = entities.get('urls', [])
        
        prompt = f"""
        Bạn là một AI phân tích lừa đảo chuyên nghiệp, hãy thật cân nhắc về các hình thức lừa đảo trên không gian mạng, đặc biệt ở Việt Nam.
        
        Hãy phân tích hình ảnh này một cách toàn diện để nhận diện các dấu hiệu lừa đảo, bao gồm:
        1. Nội dung văn bản trong hình ảnh
        2. Các yếu tố hình ảnh đáng ngờ (logo giả, thiết kế lừa đảo, v.v.)
        3. Các thông tin liên hệ và đường link
        4. Các dấu hiệu về thương hiệu, ngân hàng, hoặc tổ chức giả mạo
        
        NỘI DUNG VĂN BẢN ĐÃ TRÍCH XUẤT (nếu có):
        {text if text else 'Không có văn bản được trích xuất'}
        
        CÁC THỰC THỂ ĐÃ ĐƯỢC TRÍCH XUẤT:
        Các số điện thoại: {phones if phones else 'None found'}
        Đường dẫn URLs: {urls if urls else 'None found'}
        
        Hãy cung cấp một phân tích chi tiết bao gồm:
        1. Mức độ nguy hiểm (Low/Medium/High)
        2. Các dấu hiệu nhận biết lừa đảo từ hình ảnh
        3. Các mối lo ngại về nội dung và thiết kế
        4. Đề xuất cho người dùng để bảo vệ
        5. Mức độ tin cậy của phân tích
        
        Hãy format câu trả lời của bạn dưới dạng json gồm những nội dung sau VÀ Ở TRONG NGÔN NGỮ TIẾNG VIỆT:
        RISK_LEVEL: [Low/Medium/High]
        CONFIDENCE: [0-100]
        ANALYSIS: [Phân tích chi tiết về hình ảnh và nội dung]
        RECOMMENDATIONS: [Các hành động phải làm]
        """
        return prompt
    
    def _build_scam_analysis_prompt(self, text: str) -> str:
        """
        Build a comprehensive prompt for scam analysis
        
        Args:
            text: Extracted text from screenshot
            entities: Extracted entities
            
        Returns:
            Formatted prompt string
        """
  
        
        prompt = f"""
        Bạn là một AI phân tích lừa đảo chuyên nghiệp, hãy thật cân nhắc về các hình thức lừa đảo trên không gian mạng, đặc biệt ở Việt Nam
        Nhiệm vụ của bạn là phân tích nội dung cuộc hội thoại để xác định khả năng đây là một cuộc lừa đảo. Hãy phân tích những nội dung thu thập được từ cuộc hội thoại 
        qua điện thoại sau đây để phân tích khả năng lừa đảo (Đây là transcript nhận diện audio qua điện thoại nên đôi lúc sẽ có khoảng không nghe được)

        Nội dung đoạn hội thoại: {text} 
    
        Hãy làm ơn cung cấp một phân tích bao gồm những nội dung sau:  
        1. Mức độ nguy hiểm (Low/Medium/High)
        2. Các dấu hiệu nhận biết lừa đảo
        3. Các mối lo ngại liên quan đến đường link và số điện thoại
        4. Đề xuất cho người dùng để bảo vệ
        5. Mức độ tin cậy 
        
        Hãy format câu trả lời của bạn dưới dạng json gồm những nội dung sau:
        RISK_LEVEL: [Low/Medium/High]
        CONFIDENCE: [0-100]
        ANALYSIS: [Phân tích chi tiết]
        RECOMMENDATIONS: [Các hành động phải làm]
        """
        return prompt
    


    def _convert_to_json(self, analysis: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", analysis, re.DOTALL)
            json_str = json_match.group(1) if json_match else analysis.strip()
            return json.loads(json_str)
        except Exception:
            return {
                "message": "JSON FORMAT ERROR"
            }
