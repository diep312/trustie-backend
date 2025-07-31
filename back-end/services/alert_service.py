from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.alert import Alert
from ..models.user import User
from ..models.family import FamilyMember
from ..models.phone_number import PhoneNumber
from ..schemas import AlertCreate, Alert as AlertSchema, SeverityEnum, AlertTypeEnum
import logging

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_scam_alert(self, user_id: int, phone_number: str, risk_score: int, 
                         detection_result_id: int, message: str = None) -> Alert:
        """
        Create an alert when a scam phone number is detected
        """
        try:
            # Determine alert severity based on risk score
            severity = self._determine_severity(risk_score)
            
            # Create default message if none provided
            if not message:
                message = f"Phát hiện cuộc gọi có khả năng lừa đảo {phone_number}"
            
            alert_data = AlertCreate(
                user_id=user_id,
                alert_type=AlertTypeEnum.SCAM_DETECTED,
                severity=severity,
                message=message,
                detection_result_id=detection_result_id
            )
            
            alert = Alert(
                user_id=alert_data.user_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                detection_result_id=alert_data.detection_result_id
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            # Notify family members
            self._notify_family_members(user_id, alert)
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scam alert: {str(e)}")
            raise
    
    def create_suspicious_activity_alert(self, user_id: int, activity_description: str,
                                       detection_result_id: int) -> Alert:
        """
        Create an alert for suspicious activity
        """
        try:
            alert_data = AlertCreate(
                user_id=user_id,
                alert_type=AlertTypeEnum.SUSPICIOUS_ACTIVITY,
                severity=SeverityEnum.MEDIUM,
                message=f"Suspicious activity detected: {activity_description}",
                detection_result_id=detection_result_id
            )
            
            alert = Alert(
                user_id=alert_data.user_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                detection_result_id=alert_data.detection_result_id
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            # Notify family members
            self._notify_family_members(user_id, alert)
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating suspicious activity alert: {str(e)}")
            raise
    
    def get_user_alerts(self, user_id: int, limit: int = 50, offset: int = 0, 
                       unread_only: bool = False) -> List[Alert]:
        """
        Get alerts for a specific user
        """
        try:
            query = self.db.query(Alert).filter(Alert.user_id == user_id)
            
            if unread_only:
                query = query.filter(Alert.is_read == False)
            
            return query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {str(e)}")
            raise
    
    def mark_alert_as_read(self, alert_id: int, user_id: int) -> Alert:
        """
        Mark an alert as read
        """
        try:
            alert = self.db.query(Alert).filter(
                and_(Alert.id == alert_id, Alert.user_id == user_id)
            ).first()
            
            if not alert:
                raise ValueError(f"Alert {alert_id} not found for user {user_id}")
            
            alert.is_read = True
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking alert as read: {str(e)}")
            raise
    
    def acknowledge_alert(self, alert_id: int, user_id: int) -> Alert:
        """
        Acknowledge an alert
        """
        try:
            alert = self.db.query(Alert).filter(
                and_(Alert.id == alert_id, Alert.user_id == user_id)
            ).first()
            
            if not alert:
                raise ValueError(f"Alert {alert_id} not found for user {user_id}")
            
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error acknowledging alert: {str(e)}")
            raise
    
    def get_unread_alert_count(self, user_id: int) -> int:
        """
        Get count of unread alerts for a user
        """
        try:
            return self.db.query(Alert).filter(
                and_(Alert.user_id == user_id, Alert.is_read == False)
            ).count()
            
        except Exception as e:
            logger.error(f"Error getting unread alert count: {str(e)}")
            raise
    
    def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """
        Delete an alert
        """
        try:
            alert = self.db.query(Alert).filter(
                and_(Alert.id == alert_id, Alert.user_id == user_id)
            ).first()
            
            if not alert:
                return False
            
            self.db.delete(alert)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting alert: {str(e)}")
            raise
    
    def get_alerts_by_severity(self, user_id: int, severity: SeverityEnum) -> List[Alert]:
        """
        Get alerts by severity level
        """
        try:
            return self.db.query(Alert).filter(
                and_(Alert.user_id == user_id, Alert.severity == severity)
            ).order_by(Alert.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting alerts by severity: {str(e)}")
            raise
    
    def get_critical_alerts(self, user_id: int) -> List[Alert]:
        """
        Get critical alerts for a user
        """
        try:
            return self.db.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.severity == SeverityEnum.CRITICAL,
                    Alert.is_acknowledged == False
                )
            ).order_by(Alert.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting critical alerts: {str(e)}")
            raise
    
    def _notify_family_members(self, user_id: int, alert: Alert) -> None:
        """
        Notify family members about an alert
        This is a placeholder for actual notification logic
        """
        try:
            # Get family members who should be notified
            family_members = self.db.query(FamilyMember).filter(
                and_(
                    FamilyMember.user_id == user_id,
                    FamilyMember.notify_on_alert == True
                )
            ).all()
            
            for family_member in family_members:
                # Create alert for family member
                family_alert = Alert(
                    user_id=family_member.user_id,
                    family_member_id=family_member.linked_user_id,
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                    message=f"Cảnh báo cho người thân: {alert.message}",
                    detection_result_id=alert.detection_result_id
                )
                
                self.db.add(family_alert)
            
            self.db.commit()
            
            logger.info(f"Notified {len(family_members)} family members about alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error notifying family members: {str(e)}")
            # Don't raise here to avoid breaking the main alert creation
    
    def _determine_severity(self, risk_score: int) -> SeverityEnum:
        """
        Determine alert severity based on risk score
        """
        if risk_score >= 80:
            return SeverityEnum.CRITICAL
        elif risk_score >= 60:
            return SeverityEnum.HIGH
        elif risk_score >= 40:
            return SeverityEnum.MEDIUM
        else:
            return SeverityEnum.LOW 