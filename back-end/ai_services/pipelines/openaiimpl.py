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
        prompt = self._build_scam_analysis_prompt(text)
        
        
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
            }
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            return {"error": str(e)}
    
    def analyze_audio_scam_risk(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze audio file for scam risk using OpenAI's Whisper API for transcription
        and then analyze the transcript for scam detection
        
        Args:
            audio_path: Path to the audio file (WAV format)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Step 1: Transcribe audio using Whisper API
            with open(audio_path, "rb") as audio_file:
                transcript_response = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    language="vi"  # Vietnamese language
                )
            
            transcript = transcript_response.text
            logger.info(f"Audio transcription successful: {transcript[:100]}...")
            
            # Step 2: Analyze the transcript for scam detection
            prompt = self._build_scam_analysis_prompt(transcript)
            
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
            }
                
        except Exception as e:
            logger.error(f"Error in audio scam risk analysis: {str(e)}")
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
        Bạn là một AI phân tích lừa đảo chuyên nghiệp, am hiểu các hình thức lừa đảo trực tuyến và qua hình ảnh thường gặp ở Việt Nam.

        Nhiệm vụ:
        Phân tích hình ảnh được cung cấp để phát hiện các dấu hiệu lừa đảo tiềm ẩn. Báo cáo lại cho đối tượng người già một cách dễ hiểu và tin tưởng nhất!
        Lưu ý:
        - Nội dung văn bản được trích xuất bằng OCR có thể bị sai, lộn từ, thiếu chữ hoặc chứa nhiều nhiễu → chỉ dùng như nguồn tham khảo, không mặc định là chính xác.
        - Bạn cần kết hợp cả ngữ cảnh văn bản OCR và đặc điểm thị giác của hình ảnh (màu sắc, logo, thiết kế, bố cục, dấu hiệu giả mạo).
        - Đặc biệt chú ý tới: logo ngân hàng / tổ chức giả, đường link lạ, số điện thoại, yêu cầu cung cấp thông tin cá nhân/OTP, quảng cáo trúng thưởng.

        Dữ liệu OCR trích xuất (tham khảo, có thể sai hoặc thiếu) trong phân tích không cần đề cập tới nội dung OCR (vì người nghe sẽ là người già):
        {text if text else 'Không có văn bản được trích xuất'}

        Thông tin trích xuất thêm từ OCR:
        - Số điện thoại phát hiện: {phones if phones else 'Không có'}
        - Đường dẫn URL phát hiện: {urls if urls else 'Không có'}

        Hãy phân tích và trả lời theo định dạng JSON chuẩn, với nội dung như sau (bằng tiếng Việt):

        RISK_LEVEL: <Low|Medium|High>,      // Mức độ nguy hiểm dựa trên hình ảnh và nội dung OCR
        CONFIDENCE: <0-100>,                  // Mức tin cậy của phân tích (OCR sai nhiều thì thấp)
        ANALYSIS: <Phân tích chi tiết: mô tả các nghi vấn, dấu hiệu lừa đảo, trích dẫn dữ liệu chứng minh, nhưng xúc tích ngắn gọn dễ hiểu nhất cho người già>,
        RECOMMENDATIONS: <Các bước người dùng nên làm để tự bảo vệ>
    

        Hướng dẫn đánh giá:
        1. RISK_LEVEL:
        - High: Có nhiều bằng chứng rõ ràng của scam (logo giả, cảnh báo ngân hàng, yêu cầu OTP, link đáng ngờ…)
        - Medium: Có vài yếu tố khả nghi nhưng chưa xác thực đầy đủ
        - Low: Nội dung hình ảnh không thể hiện nguy cơ lừa đảo rõ ràng
        2. CONFIDENCE:
        - Xem xét độ nhiễu của OCR và khả năng phân tích từ hình ảnh
        - Có thể OCR sai nhiều, xem xét hình ảnh
        3. ANALYSIS:
        - Nêu cả bằng chứng từ hình ảnh và từ OCR
        - Giải thích tại sao đánh giá như vậy
        4. RECOMMENDATIONS:
        - Cụ thể, hành động rõ ràng (không nhập thông tin cá nhân, không bấm vào link, xác minh qua kênh chính thức)
        """
        return prompt
    
    def _build_scam_analysis_prompt(self, text: str) -> str:
        """
        Build a comprehensive prompt for scam analysis
        
        Args:
            text: transcript            
        Returns:
            Formatted prompt string
        """
  
        
        prompt = f"""
        Bạn là một AI chuyên gia phân tích lừa đảo trong lĩnh vực an ninh mạng, đặc biệt am hiểu các hình thức lừa đảo phổ biến ở Việt Nam.

        Nhiệm vụ:
        Phân tích nội dung của một cuộc hội thoại điện thoại để đánh giá khả năng đây là một cuộc lừa đảo, và bạn phải truyền đạt lại thông tin dành cho đối tượng người già, giải thích dễ hiểu nhất có thể và tạo lòng tin với họ.  
        Những dữ liệu hội thoại này được tạo bởi mô hình nhận dạng giọng nói (speech-to-text) - không nên thêm thông tin phân tích về text-to-speech chi tiết vào trong phân tích - chỉ nên bảo là chưa nghe rõ hay sao, do đó:
        - Nhiều đoạn có thể chứa từ ngữ vô nghĩa hoặc không liên quan (gibberish) → bỏ qua.
        - Cuộc hội thoại đang có thể tiếp tục diễn ra, nếu như bạn cảm thấy chưa đủ thông tin thì chưa nâng mức risk lên cao nhất, khi nào chắc chắn thì nâng lên 
        - Có thể có lỗi nhận diện âm tiết, lặp lại từ, hoặc thiếu hụt một số đoạn.
        - Bạn cần suy luận và khớp bối cảnh tổng thể từ các phần thông tin hữu ích.
        - Tập trung nhận biết từ khóa, cụm từ, nội dung liên quan đến các thủ đoạn lừa đảo phổ biến đặc biệt là ở Việt Nam (gọi yêu cầu cung cấp OTP, thông tin ngân hàng, hăm dọa, báo tin trúng thưởng, link giả mạo, v.v.).
        - Nếu nên can thiệp và dừng cuộc gọi hãy cảnh cáo ở mức nguy cơ High - giúp đỡ người già không bị thao túng tâm lý

        Dữ liệu hội thoại cần phân tích: 
        {text}

        
        Phân tích và đưa ra kết quả dưới dạng JSON **đúng cấu trúc sau**:
        RISK_LEVEL: <Low|Medium|High>,       //Mức độ nguy hiểm
        CONFIDENCE: <0-100>,                   // Mức độ tin cậy dựa trên chất lượng transcript
        ANALYSIS: <Phân tích chi tiết nội dung và dấu hiệu, nhưng xúc tích ngắn gọn dễ hiểu nhất cho người già>,
        RECOMMENDATIONS: <Các hành động người dùng nên làm để bảo vệ>
    

        Hướng dẫn đánh giá:
        1. **RISK_LEVEL**: Chỉ chọn High nếu xuất hiện nhiều tín hiệu rõ ràng (yêu cầu OTP, tài khoản ngân hàng, đe dọa phong tỏa, link lạ...), Medium nếu có một vài dấu hiệu nhưng thông tin chưa đủ chắc chắn, Low nếu không có tín hiệu nghi vấn rõ rệt.
        2. **CONFIDENCE**: Cân nhắc rằng transcript có thể sai sót; nếu bối cảnh chỉ suy luận được phần nào thì CONFIDENCE thấp hơn.
        3. **ANALYSIS**: Phân tích cả khả năng xảy ra lừa đảo, có thể trích các từ khóa quan trọng nghe được, và giải thích tại sao.
        4. **RECOMMENDATIONS**: Đưa ra các bước hành động cụ thể (VD: không cung cấp OTP, không bấm link, gọi tổng đài chính thức kiểm tra...).
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
