import requests
from typing import Dict, Any


import requests
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import os
from .llmsbase import LLMServiceBase




class GeminiService(LLMServiceBase):
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM service with API key
        Args:
            api_key: Optional API key, will load from environment if not provided
        """
        super().__init__(api_key=api_key, api_key_env="GEMINI_API_KEY")
        self.base_model = "gemini-2.0-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.base_model}:generateContent"
    
    
    def analyze_image_scam_risk(self, image_path: str, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze image for scam or fraud risk using Gemini LLM with multimodal capabilities
        
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
            
            # Prepare multimodal content
            content = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": self._get_mime_type(image_path),
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            response = self._call_gemini_api_multimodal(content)
            
            if response.get("status_code") == 200:
                result = response.get("data", {})
                analysis = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {
                    "analysis": analysis,
                    "risk_level": self._extract_risk_level(analysis),
                    "confidence": self._extract_confidence(analysis),
                    "model_used": self.base_model,
                    "image_analyzed": True
                }
            else:
                logger.error(f"Gemini API error: {response.get('error', 'Unknown error')}")
                return {"error": response.get('error', 'API call failed')}
                
        except Exception as e:
            logger.error(f"Error in image scam risk analysis: {str(e)}")
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
    
    def _call_gemini_api_multimodal(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make multimodal API call to Gemini with image and text
        
        Args:
            content: The multimodal content to send to Gemini
            
        Returns:
            Dictionary containing response data
        """
        try:
            response = requests.post(
                self.base_url,
                params={"key": self.api_key},
                json=content,
                timeout=60  # Increased timeout for image processing
            )
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "status_code": 500,
                "error": f"Request failed: {str(e)}"
            }
    
    def _build_scam_analysis_prompt(self, text: str, entities: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt for scam analysis
        
        Args:
            text: Extracted text from screenshot
            entities: Extracted entities
            
        Returns:
            Formatted prompt string
        """
        phones = entities.get('phones', [])
        urls = entities.get('urls', [])
        
        prompt = f"""
        Bạn là một AI phân tích lừa đảo chuyên nghiệp, hãy thật cân nhắc về các hình thức lừa đảo trên không gian mạng, đặc biệt ở Việt Nam
        Hãy phân tích những nội dung thu thập từ một cuộc hội thoại giữa người dùng và một số điện thoại lạ mặt. 
        
        
        NỘI DUNG MÀ CẦN PHẢI PHÂN TÍCH:
        {text}
        
        CÁC THỰC THỂ MÀ ĐÃ ĐƯỢC TRÍCH XUẤT:
        Các số điện thoại: {phones if phones else 'None found'}
        Đường dẫn URLs: {urls if urls else 'None found'}
        

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
    
    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """
        Make API call to Gemini
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Dictionary containing response data
        """
        try:
            response = requests.post(
                self.base_url,
                params={"key": self.api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "status_code": 500,
                "error": f"Request failed: {str(e)}"
            }
    
    def _extract_risk_level(self, analysis: str) -> str:
        """
        Extract risk level from analysis text
        
        Args:
            analysis: Analysis text from LLM
            
        Returns:
            Risk level (Low/Medium/High)
        """
        analysis_lower = analysis.lower()
        if "high" in analysis_lower:
            return "High"
        elif "medium" in analysis_lower:
            return "Medium"
        else:
            return "Low"
    
    def _extract_confidence(self, analysis: str) -> int:
        """
        Extract confidence level from analysis text
        
        Args:
            analysis: Analysis text from LLM
            
        Returns:
            Confidence level (0-100)
        """
        import re
        confidence_match = re.search(r'CONFIDENCE: \s*(\d+)', analysis, re.IGNORECASE)
        if confidence_match:
            return int(confidence_match.group(1))
        return 0  # Default confidence if not found
    
    def analyze_text_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        General text analysis method
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        prompts = {
            "general": f"Analyze the following text and provide insights: {text}",
            "sentiment": f"Analyze the sentiment of this text: {text}",
            "summary": f"Provide a summary of this text: {text}"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        response = self._call_gemini_api(prompt)
        
        if response.get("status_code") == 200:
            result = response.get("data", {})
            analysis = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return {"analysis": analysis, "type": analysis_type}
        else:
            return {"error": response.get('error', 'Analysis failed')}
