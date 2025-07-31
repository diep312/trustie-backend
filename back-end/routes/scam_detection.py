from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..database import get_db
from ..services.scam_detection_service import ScamDetectionService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scam-detection", tags=["scam-detection"])

# Request/Response models
class ScamDetectionRequest(BaseModel):
    phone_number: str
    user_id: int
    context: Optional[str] = None  # Additional context about the call/message

class ScamDetectionResponse(BaseModel):
    phone_check: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    detection_result_id: int
    scan_request_id: int
    alert_created: bool
    alert_id: Optional[int] = None
    recommendation: str

class DetectionHistoryResponse(BaseModel):
    scan_requests: int
    detection_results: int
    alerts: int
    recent_scans: list

@router.post("/detect", response_model=ScamDetectionResponse)
async def detect_scam(
    request: ScamDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Comprehensive scam detection for phone numbers
    This endpoint performs:
    1. Database lookup for flagged numbers
    2. AI analysis of the phone number
    3. Risk assessment and scoring
    4. Alert creation if scam detected
    5. Family member notification
    """
    try:
        scam_detection_service = ScamDetectionService(db)
        
        result = scam_detection_service.detect_scam_from_phone(
            phone_number=request.phone_number,
            user_id=request.user_id,
            context=request.context
        )
        
        return ScamDetectionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in scam detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history/{user_id}", response_model=DetectionHistoryResponse)
async def get_detection_history(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get user's scam detection history
    """
    try:
        scam_detection_service = ScamDetectionService(db)
        history = scam_detection_service.get_detection_history(user_id, limit)
        
        return DetectionHistoryResponse(**history)
        
    except Exception as e:
        logger.error(f"Error getting detection history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/{user_id}")
async def get_detection_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get scam detection statistics for a user
    """
    try:
        scam_detection_service = ScamDetectionService(db)
        history = scam_detection_service.get_detection_history(user_id)
        
        # Calculate additional stats
        total_scans = history["scan_requests"]
        total_alerts = history["alerts"]
        total_detections = history["detection_results"]
        
        # Calculate success rate (alerts / scans)
        success_rate = (total_alerts / total_scans * 100) if total_scans > 0 else 0
        
        return {
            "total_scans": total_scans,
            "total_alerts": total_alerts,
            "total_detections": total_detections,
            "success_rate": round(success_rate, 2),
            "recent_activity": len(history["recent_scans"])
        }
        
    except Exception as e:
        logger.error(f"Error getting detection stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/bulk-check")
async def bulk_check_phone_numbers(
    phone_numbers: list[str],
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Check multiple phone numbers at once
    """
    try:
        scam_detection_service = ScamDetectionService(db)
        results = []
        
        for phone_number in phone_numbers:
            try:
                result = scam_detection_service.detect_scam_from_phone(
                    phone_number=phone_number,
                    user_id=user_id
                )
                results.append({
                    "phone_number": phone_number,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "phone_number": phone_number,
                    "error": str(e)
                })
        
        return {
            "total_checked": len(phone_numbers),
            "successful_checks": len([r for r in results if "result" in r]),
            "failed_checks": len([r for r in results if "error" in r]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk phone check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/risk-assessment/{phone_number}")
async def get_risk_assessment(
    phone_number: str,
    context: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get detailed risk assessment for a phone number without creating alerts
    """
    try:
        scam_detection_service = ScamDetectionService(db)
        
        # Create a temporary service instance for analysis only
        phone_service = scam_detection_service.phone_service
        
        # Check database
        phone_check = phone_service.check_phone_number(phone_number)
        
        # Perform AI analysis
        ai_analysis = scam_detection_service._perform_ai_analysis(phone_number, context)
        
        # Calculate overall risk
        db_risk = phone_check.get("risk_score", 0)
        ai_risk = ai_analysis["risk_score"]
        overall_risk = max(db_risk, ai_risk)
        
        # Determine risk level
        if overall_risk >= 80:
            risk_level = "CRITICAL"
        elif overall_risk >= 60:
            risk_level = "HIGH"
        elif overall_risk >= 40:
            risk_level = "MEDIUM"
        elif overall_risk >= 20:
            risk_level = "LOW"
        else:
            risk_level = "SAFE"
        
        return {
            "phone_number": phone_number,
            "database_check": phone_check,
            "ai_analysis": ai_analysis,
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "recommendation": scam_detection_service._get_recommendation(ai_analysis, phone_check)
        }
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 