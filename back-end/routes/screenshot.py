from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services.screenshot_service import ScreenshotService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screenshot", tags=["screenshot"])

@router.post("/analyze")
async def analyze_screenshot(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a screenshot, extract text, analyze for scam, and return result.
    """
    try:
        service = ScreenshotService(db)
        result = service.process_screenshot(file, user_id, description)
        return result
    except Exception as e:
        logger.error(f"Error analyzing screenshot: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")