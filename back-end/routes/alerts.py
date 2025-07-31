from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.alert_service import AlertService
from ..schemas import Alert as AlertSchema, SeverityEnum, AlertTypeEnum
from ..models.alert import Alert
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Request/Response models
class CreateAlertRequest(BaseModel):
    user_id: int
    alert_type: AlertTypeEnum
    severity: SeverityEnum = SeverityEnum.MEDIUM
    message: str
    detection_result_id: int
    family_member_id: Optional[int] = None

class AlertResponse(BaseModel):
    id: int
    user_id: int
    alert_type: str
    severity: str
    message: str
    is_read: bool
    is_acknowledged: bool
    created_at: str

@router.get("/user/{user_id}", response_model=List[AlertResponse])
async def get_user_alerts(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get alerts for a specific user
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.get_user_alerts(
            user_id=user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        return [AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        ) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error getting user alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/unread-count")
async def get_unread_alert_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get count of unread alerts for a user
    """
    try:
        alert_service = AlertService(db)
        count = alert_service.get_unread_alert_count(user_id)
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error getting unread alert count: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Mark an alert as read
    """
    try:
        alert_service = AlertService(db)
        alert = alert_service.mark_alert_as_read(alert_id, user_id)
        
        return AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking alert as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert
    """
    try:
        alert_service = AlertService(db)
        alert = alert_service.acknowledge_alert(alert_id, user_id)
        
        return AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Delete an alert
    """
    try:
        alert_service = AlertService(db)
        deleted = alert_service.delete_alert(alert_id, user_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/severity/{severity}", response_model=List[AlertResponse])
async def get_alerts_by_severity(
    user_id: int,
    severity: SeverityEnum,
    db: Session = Depends(get_db)
):
    """
    Get alerts by severity level
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.get_alerts_by_severity(user_id, severity)
        
        return [AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        ) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error getting alerts by severity: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/critical", response_model=List[AlertResponse])
async def get_critical_alerts(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get critical alerts for a user
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.get_critical_alerts(user_id)
        
        return [AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        ) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error getting critical alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/create", response_model=AlertResponse)
async def create_alert(
    request: CreateAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new alert
    """
    try:
        alert_service = AlertService(db)
        
        # Create alert based on type
        if request.alert_type == AlertTypeEnum.SCAM_DETECTED:
            # This would typically be called from phone check endpoint
            raise HTTPException(status_code=400, detail="Use phone check endpoint for scam alerts")
        else:
            # For other alert types, create directly
            alert = Alert(
                user_id=request.user_id,
                family_member_id=request.family_member_id,
                alert_type=request.alert_type,
                severity=request.severity,
                message=request.message,
                detection_result_id=request.detection_result_id
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
        
        return AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
            is_acknowledged=alert.is_acknowledged,
            created_at=alert.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/user/{user_id}/mark-all-read")
async def mark_all_alerts_as_read(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark all alerts for a user as read
    """
    try:
        alert_service = AlertService(db)
        alerts = alert_service.get_user_alerts(user_id, unread_only=True)
        
        for alert in alerts:
            alert_service.mark_alert_as_read(alert.id, user_id)
        
        return {"message": f"Marked {len(alerts)} alerts as read"}
        
    except Exception as e:
        logger.error(f"Error marking all alerts as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 