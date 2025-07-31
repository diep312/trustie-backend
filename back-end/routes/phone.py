from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.phone_service import PhoneService
from ..services.alert_service import AlertService
from ..schemas import PhoneNumberCreate, PhoneNumber as PhoneNumberSchema
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phone", tags=["phone"])

# Request/Response models
class PhoneCheckRequest(BaseModel):
    phone_number: str
    user_id: Optional[int] = None

class PhoneCheckResponse(BaseModel):
    found: bool
    is_flagged: bool
    flag_reason: Optional[str] = None
    risk_score: int
    info: Optional[str] = None
    origin: Optional[str] = None
    last_checked: Optional[datetime] = None
    created_at: Optional[datetime] = None
    message: Optional[str] = None

class FlagPhoneRequest(BaseModel):
    phone_number: str
    flag_reason: str
    risk_score: int = 50

class PhoneSearchRequest(BaseModel):
    query: str
    limit: int = 50


# ROUTE 

@router.post("/check", response_model=PhoneCheckResponse)
async def check_phone_number(
    request: PhoneCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a phone number is flagged in the database
    """
    try:
        phone_service = PhoneService(db)
        result = phone_service.check_phone_number(
            phone_number=request.phone_number,
            user_id=request.user_id
        )
        
        return PhoneCheckResponse(**result)
        
    except Exception as e:
        logger.error(f"Error checking phone number: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/flag", response_model=PhoneNumberSchema)
async def flag_phone_number(
    request: FlagPhoneRequest,
    db: Session = Depends(get_db)
):
    """
    Flag a phone number as suspicious or scam
    """
    try:
        phone_service = PhoneService(db)
        phone_record = phone_service.flag_phone_number(
            phone_number=request.phone_number,
            flag_reason=request.flag_reason,
            risk_score=request.risk_score
        )
        
        return PhoneNumberSchema.from_orm(phone_record)
        
    except Exception as e:
        logger.error(f"Error flagging phone number: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/add", response_model=PhoneNumberSchema)
async def add_phone_number(
    phone_data: PhoneNumberCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new phone number to the database
    """
    try:
        phone_service = PhoneService(db)
        phone_record = phone_service.add_phone_number(phone_data)
        
        return PhoneNumberSchema.from_orm(phone_record)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding phone number: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/flagged", response_model=List[PhoneNumberSchema])
async def get_flagged_phones(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all flagged phone numbers
    """
    try:
        phone_service = PhoneService(db)
        phones = phone_service.get_flagged_phones(limit=limit, offset=offset)
        
        return [PhoneNumberSchema.from_orm(phone) for phone in phones]
        
    except Exception as e:
        logger.error(f"Error getting flagged phones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{phone_id}", response_model=PhoneNumberSchema)
async def get_phone_by_id(
    phone_id: int,
    db: Session = Depends(get_db)
):
    """
    Get phone number by ID
    """
    try:
        phone_service = PhoneService(db)
        phone = phone_service.get_phone_by_id(phone_id)
        
        if not phone:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        return PhoneNumberSchema.from_orm(phone)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phone by ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{phone_id}/risk-score", response_model=PhoneNumberSchema)
async def update_phone_risk_score(
    phone_id: int,
    risk_score: int = Query(..., ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Update the risk score of a phone number
    """
    try:
        phone_service = PhoneService(db)
        phone = phone_service.update_phone_risk_score(phone_id, risk_score)
        
        return PhoneNumberSchema.from_orm(phone)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating phone risk score: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search", response_model=List[PhoneNumberSchema])
async def search_phones(
    request: PhoneSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search phone numbers by number, info, or origin
    """
    try:
        phone_service = PhoneService(db)
        phones = phone_service.search_phones(
            query=request.query,
            limit=request.limit
        )
        
        return [PhoneNumberSchema.from_orm(phone) for phone in phones]
        
    except Exception as e:
        logger.error(f"Error searching phones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=List[PhoneNumberSchema])
async def get_user_phones(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all phone numbers associated with a user
    """
    try:
        phone_service = PhoneService(db)
        phones = phone_service.get_user_phones(user_id)
        
        return [PhoneNumberSchema.from_orm(phone) for phone in phones]
        
    except Exception as e:
        logger.error(f"Error getting user phones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/check-and-alert")
async def check_phone_and_create_alert(
    request: PhoneCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check phone number and create alert if flagged
    """
    try:
        phone_service = PhoneService(db)
        alert_service = AlertService(db)
        
        # Check the phone number
        result = phone_service.check_phone_number(
            phone_number=request.phone_number,
            user_id=request.user_id
        )
        
        # If phone is flagged and user_id is provided, create alert
        if result["found"] and result["is_flagged"] and request.user_id:
            # Create a dummy detection result ID (in real app, this would come from AI analysis)
            detection_result_id = 1  # This should be replaced with actual detection result
            
            alert = alert_service.create_scam_alert(
                user_id=request.user_id,
                phone_number=request.phone_number,
                risk_score=result["risk_score"],
                detection_result_id=detection_result_id
            )
            
            return {
                "phone_check": result,
                "alert_created": True,
                "alert_id": alert.id
            }
        
        return {
            "phone_check": result,
            "alert_created": False
        }
        
    except Exception as e:
        logger.error(f"Error checking phone and creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 