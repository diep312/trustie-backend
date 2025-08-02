from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse
import logging
from ..ai_services.services import ai_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text-to-speech", tags=["text-to-speech"])

@router.post("/")
async def text_to_speech(text: str = Form(...)):
    """
    Convert text to speech and return the audio file
    
    - **text**: Text to convert to speech (required)
    """
    try:
        # Validate text
        if not text.strip():
            raise HTTPException(status_code=400, detail="Không được để trống văn bản")
        
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Văn bản quá dài (quá 1000 từ)")
        
        # Generate TTS
        result = ai_services.text_to_speech(text=text)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "TTS bị lỗi"))
        
        # Return the audio file directly
        return FileResponse(
            path=result["file_path"],
            media_type="audio/wav",
            filename=result["file_name"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 