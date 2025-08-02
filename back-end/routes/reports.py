from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.report_service import ReportService
from ..schemas import Report as ReportSchema
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])

# Request models
class PhoneReportRequest(BaseModel):
    phone_number: str
    reason: str
    user_id: int
    priority: str = "medium"

class WebsiteReportRequest(BaseModel):
    domain: str
    reason: str
    user_id: int
    priority: str = "medium"
    url: Optional[str] = None

class SMSReportRequest(BaseModel):
    sender_phone: str
    reason: str
    user_id: int
    priority: str = "medium"
    message_body: Optional[str] = None

class UpdateReportStatusRequest(BaseModel):
    status: str
    admin_notes: Optional[str] = None

# Response models
class ReportResponse(BaseModel):
    id: int
    reason: str
    report_type: str
    status: str
    priority: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    user_id: int
    reported_phone_id: Optional[int] = None
    reported_website_id: Optional[int] = None
    reported_sms_id: Optional[int] = None

    class Config:
        from_attributes = True

# ROUTES

@router.post("/phone", response_model=ReportResponse)
async def report_phone(
    request: PhoneReportRequest,
    db: Session = Depends(get_db)
):
    """
    Report a phone number. If the phone doesn't exist, it will be created.
    """
    try:
        report_service = ReportService(db)
        report = report_service.report_phone(
            phone_number=request.phone_number,
            reason=request.reason,
            user_id=request.user_id,
            priority=request.priority
        )
        
        return ReportResponse.from_orm(report)
        
    except Exception as e:
        logger.error(f"Error creating phone report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/website", response_model=ReportResponse)
async def report_website(
    request: WebsiteReportRequest,
    db: Session = Depends(get_db)
):
    """
    Report a website. If the website doesn't exist, it will be created.
    """
    try:
        report_service = ReportService(db)
        report = report_service.report_website(
            domain=request.domain,
            reason=request.reason,
            user_id=request.user_id,
            priority=request.priority,
            url=request.url
        )
        
        return ReportResponse.from_orm(report)
        
    except Exception as e:
        logger.error(f"Error creating website report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/sms", response_model=ReportResponse)
async def report_sms(
    request: SMSReportRequest,
    db: Session = Depends(get_db)
):
    """
    Report a phone number that sent suspicious SMS. If the phone doesn't exist, it will be created.
    """
    try:
        report_service = ReportService(db)
        report = report_service.report_sms(
            sender_phone=request.sender_phone,
            reason=request.reason,
            user_id=request.user_id,
            priority=request.priority,
            message_body=request.message_body
        )
        
        return ReportResponse.from_orm(report)
        
    except Exception as e:
        logger.error(f"Error creating SMS report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# @router.get("/user/{user_id}", response_model=List[ReportResponse])
# async def get_user_reports(
#     user_id: int,
#     limit: int = Query(50, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get all reports by a specific user
#     """
#     try:
#         report_service = ReportService(db)
#         reports = report_service.get_user_reports(
#             user_id=user_id,
#             limit=limit,
#             offset=offset
#         )
        
#         return [ReportResponse.from_orm(report) for report in reports]
        
#     except Exception as e:
#         logger.error(f"Error getting user reports: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.get("/type/{report_type}", response_model=List[ReportResponse])
# async def get_reports_by_type(
#     report_type: str,
#     limit: int = Query(50, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get all reports of a specific type (phone, website, sms)
#     """
#     try:
#         if report_type not in ["phone", "website", "sms"]:
#             raise HTTPException(status_code=400, detail="Invalid report type. Must be 'phone', 'website', or 'sms'")
        
#         report_service = ReportService(db)
#         reports = report_service.get_reports_by_type(
#             report_type=report_type,
#             limit=limit,
#             offset=offset
#         )
        
#         return [ReportResponse.from_orm(report) for report in reports]
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error getting reports by type: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.get("/{report_id}", response_model=ReportResponse)
# async def get_report_by_id(
#     report_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get a specific report by ID
#     """
#     try:
#         report_service = ReportService(db)
#         report = report_service.get_report_by_id(report_id)
        
#         if not report:
#             raise HTTPException(status_code=404, detail="Report not found")
        
#         return ReportResponse.from_orm(report)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error getting report by ID: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.put("/{report_id}/status", response_model=ReportResponse)
# async def update_report_status(
#     report_id: int,
#     request: UpdateReportStatusRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Update the status of a report (admin function)
#     """
#     try:
#         valid_statuses = ["pending", "reviewed", "resolved", "dismissed"]
#         if request.status not in valid_statuses:
#             raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
#         report_service = ReportService(db)
#         report = report_service.update_report_status(
#             report_id=report_id,
#             status=request.status,
#             admin_notes=request.admin_notes
#         )
        
#         return ReportResponse.from_orm(report)
        
#     except HTTPException:
#         raise
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         logger.error(f"Error updating report status: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error") 