from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.report import Report
from ..models.phone_number import PhoneNumber
from ..models.website import Website
from ..models.sms_msg import SMSLog
from ..models.user import User
from ..schemas import ReportCreate, Report as ReportSchema
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def report_phone(self, phone_number: str, reason: str, user_id: int, priority: str = "medium") -> Report:
        """
        Report a phone number. If the phone doesn't exist, create it first.
        """
        try:
            # Clean the phone number
            cleaned_number = self._clean_phone_number(phone_number)
            
            # Check if phone number exists
            phone_record = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()
            
            # If phone doesn't exist, create it
            if not phone_record:
                phone_record = PhoneNumber(
                    number=cleaned_number,
                    info=f"Được báo cáo bởi người dùng {user_id}",
                    origin="user_report",
                    is_flagged=false,
                    flag_reason="",
                    risk_score=50
                )
                self.db.add(phone_record)
                self.db.flush()  # Get the ID without committing
            
            # Create the report
            report = Report(
                reason=reason,
                report_type="phone",
                status="pending",
                priority=priority,
                user_id=user_id,
                reported_phone_id=phone_record.id
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Phone report created: {report.id} for phone {cleaned_number}")
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating phone report: {str(e)}")
            raise
    
    def report_website(self, domain: str, reason: str, user_id: int, priority: str = "medium", url: Optional[str] = None) -> Report:
        """
        Report a website. If the website doesn't exist, create it first.
        """
        try:
            # Clean the domain
            cleaned_domain = self._clean_domain(domain)
            
            # Check if website exists
            website_record = self.db.query(Website).filter(
                Website.domain == cleaned_domain
            ).first()
            
            # If website doesn't exist, create it
            if not website_record:
                website_record = Website(
                    domain=cleaned_domain,
                    url=url,
                    description=f"Được báo cáo bởi người dùng {user_id}",
                    trust_worthy_point=0.0,
                    risk_score=50,
                    is_flagged=False,
                    flag_reason=""
                )
                self.db.add(website_record)
                self.db.flush()  # Get the ID without committing
            
            # Create the report
            report = Report(
                reason=reason,
                report_type="website",
                status="pending",
                priority=priority,
                user_id=user_id,
                reported_website_id=website_record.id
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Website report created: {report.id} for domain {cleaned_domain}")
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating website report: {str(e)}")
            raise
    
    def report_sms(self, sender_phone: str, reason: str, user_id: int, priority: str = "medium", message_body: Optional[str] = None) -> Report:
        """
        Report a phone number that sent suspicious SMS. If the phone doesn't exist, create it first.
        """
        try:
            # Clean the phone number
            cleaned_number = self._clean_phone_number(sender_phone)
            
            # Check if phone number exists
            phone_record = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()
            
            # If phone doesn't exist, create it
            if not phone_record:
                phone_record = PhoneNumber(
                    number=cleaned_number,
                    info=f"Được báo cáo hành vi bất thường bởi người dùngdùng {user_id}",
                    origin="sms_report",
                    is_flagged=False,
                    flag_reason="Đã được báo cáo hành vi bất thường",
                    risk_score=50
                )
                self.db.add(phone_record)
                self.db.flush()  # Get the ID without committing
            
            # If message_body is provided, also create an SMS log entry
            sms_record = None
            if message_body:
                sms_record = SMSLog(
                    message_body=message_body,
                    sender=cleaned_number,
                    is_flagged=False,
                    flag_reason="",
                    risk_score=50,
                    message_type="incoming",
                    user_id=user_id,
                    phone_id=phone_record.id
                )
                self.db.add(sms_record)
                self.db.flush()  # Get the ID without committing
            
            # Create the report (linked to phone number, optionally to SMS)
            report = Report(
                reason=reason,
                report_type="sms",
                status="pending",
                priority=priority,
                user_id=user_id,
                reported_phone_id=phone_record.id,
                reported_sms_id=sms_record.id if sms_record else None
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"SMS report created: {report.id} for phone {cleaned_number}")
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating SMS report: {str(e)}")
            raise
    
    def get_user_reports(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Report]:
        """
        Get all reports by a specific user
        """
        try:
            reports = self.db.query(Report).filter(
                Report.user_id == user_id
            ).order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting user reports: {str(e)}")
            raise
    
    def get_reports_by_type(self, report_type: str, limit: int = 50, offset: int = 0) -> List[Report]:
        """
        Get all reports of a specific type
        """
        try:
            reports = self.db.query(Report).filter(
                Report.report_type == report_type
            ).order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting reports by type: {str(e)}")
            raise
    
    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """
        Get a specific report by ID
        """
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            return report
            
        except Exception as e:
            logger.error(f"Error getting report by ID: {str(e)}")
            raise
    
    def update_report_status(self, report_id: int, status: str, admin_notes: Optional[str] = None) -> Report:
        """
        Update the status of a report
        """
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ValueError(f"Report with ID {report_id} not found")
            
            report.status = status
            if admin_notes:
                report.admin_notes = admin_notes
            
            if status in ["resolved", "dismissed"]:
                report.resolved_at = datetime.utcnow()
            
            report.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(report)
            
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating report status: {str(e)}")
            raise
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """
        Clean phone number by removing spaces, dashes, and other non-digit characters
        """
        import re
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        return cleaned
    
    def _clean_domain(self, domain: str) -> str:
        """
        Clean domain by removing protocol and path
        """
        import re
        # Remove protocol (http://, https://)
        cleaned = re.sub(r'^https?://', '', domain.lower())
        # Remove path and query parameters
        cleaned = cleaned.split('/')[0]
        # Remove www. prefix
        cleaned = re.sub(r'^www\.', '', cleaned)
        return cleaned