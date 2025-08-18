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
                         detection_result_id: Optional[int] = None, message: str = None) -> Alert:
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
    
    def create_phone_based_alert(self, user_id: int, phone_number: str, risk_score: int, 
                                flag_reason: str = None, message: str = None) -> Alert:
        """
        Create an alert when a phone number is checked and found to be high risk
        This method is used when alerts are created without AI detection results
        """
        try:
            # Determine alert severity based on risk score
            severity = self._determine_severity(risk_score)
            
            # Create default message if none provided
            if not message:
                if flag_reason:
                    message = f"Cuộc gọi {phone_number} có dấu hiệu bất thường. Lý do: {flag_reason}"
                else:
                    message = f"Cuộc gọi {phone_number} có dấu hiệu bất thường. Xin hãy cẩn thận và không chia sẻ thông tin cá nhân"
            
            alert_data = AlertCreate(
                user_id=user_id,
                alert_type=AlertTypeEnum.PHONE_RISK,
                severity=severity,
                message=message
                # detection_result_id is None for phone-based alerts
            )
            
            alert = Alert(
                user_id=alert_data.user_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                detection_result_id=None
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            # Notify family members
            self._notify_family_members(user_id, alert)
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating phone-based alert: {str(e)}")
            raise
    
    def create_suspicious_activity_alert(self, user_id: int, activity_description: str,
                                       detection_result_id: Optional[int] = None) -> Alert:
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
        Get alerts for a specific user:
        - Direct alerts (Alert.user_id matches the user)
        - Alerts linked via FamilyMember relationship
        """
        try:
            # Subquery to find FamilyMember IDs where this user is the linked account
            linked_family_ids_subq = self.db.query(FamilyMember.id).filter(
                FamilyMember.linked_user_id == user_id
            )

            query = self.db.query(Alert).filter(
                or_(
                    Alert.user_id == user_id,  # Direct alerts for this user
                    Alert.family_member_id.in_(linked_family_ids_subq)  # Alerts sent because of link
                )
            )

            if unread_only:
                query = query.filter(Alert.is_read == False)

            return (query
                    .order_by(Alert.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                    )

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
                    user_id=family_member.linked_user_id,
                    family_member_id=user_id,  # This links back to the elderly user
                    alert_type=AlertTypeEnum.FAMILY_MEMBER_ALERT,
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
    
    def create_family_member_alert(self, elderly_user_id: int, family_member_id: int, 
                                 phone_number: str, risk_score: int, flag_reason: str = None) -> Alert:
        """
        Create a specific alert for family members when elderly user receives high-risk calls
        """
        try:
            severity = self._determine_severity(risk_score)
            
            message = f"Người thân của bạn đã nhận cuộc gọi từ số {phone_number} có nghi vấn lừa đảo. Chúng tôi khuyến nghị bạn liên hệ để kiểm tra"
            if flag_reason:
                message += f"Lý do: {flag_reason}"

            
            alert_data = AlertCreate(
                user_id=family_member_id,
                family_member_id=elderly_user_id,
                alert_type=AlertTypeEnum.FAMILY_MEMBER_ALERT,
                severity=severity,
                message=message
            )
            
            alert = Alert(
                user_id=alert_data.user_id,
                family_member_id=alert_data.family_member_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                detection_result_id=None
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Created family member alert {alert.id} for user {family_member_id} about elderly user {elderly_user_id}")
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating family member alert: {str(e)}")
            raise
    
    def create_family_only_alert(self, elderly_user_id: int, family_member_id: int, 
                               phone_number: str, risk_score: int, flag_reason: str = None) -> Alert:
        """
        Create an alert ONLY for family members when elderly user receives medium-high risk calls (60-79)
        This alert is not shown to the elderly user to avoid unnecessary alarm
        """
        try:
            severity = self._determine_severity(risk_score)
            
            message = f"Người thân của bạn đã nhận cuộc gọi từ số {phone_number} có nguy cơ trung bình-cao"
            if flag_reason:
                message += f": {flag_reason}"
            message += " (Chỉ thông báo cho gia đình)"
            
            alert_data = AlertCreate(
                user_id=family_member_id,
                family_member_id=elderly_user_id,
                alert_type=AlertTypeEnum.FAMILY_ONLY_ALERT,
                severity=severity,
                message=message
            )
            
            alert = Alert(
                user_id=alert_data.user_id,
                family_member_id=alert_data.family_member_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                message=alert_data.message,
                detection_result_id=None
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Created family-only alert {alert.id} for user {family_member_id} about elderly user {elderly_user_id}")
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating family-only alert: {str(e)}")
            raise
    
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