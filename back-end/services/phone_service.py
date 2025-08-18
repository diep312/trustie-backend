from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.phone_number import PhoneNumber
from ..models.user import User
from ..models.alert import Alert
from ..models.family import FamilyMember
from ..schemas import PhoneNumberCreate, PhoneNumber as PhoneNumberSchema
from ..services.alert_service import AlertService
import logging
import re

logger = logging.getLogger(__name__)

class PhoneService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_phone_number(self, phone_number: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Check if a phone number is flagged in the database.
        If not found, add to DB and run simple potential scam check (demo).
        If high risk and user_id provided, create alerts for user and family members.
        """
        try:
            cleaned_number = self._clean_phone_number(phone_number)

            phone_record = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()

            if phone_record:
                # Update last_checked
                phone_record.last_checked = datetime.utcnow()
                self.db.commit()
                
                # Check if we should create alerts based on risk score
                if user_id: 
                    if phone_record.is_flagged:
                        self._create_alerts_for_high_risk_phone(user_id, phone_record)
                
                    if phone_record.risk_score >= 60 and phone_record <= 80:
                        self._create_family_only_alerts(user_id, phone_record)
                
                return {
                    "found": True,
                    "is_flagged": phone_record.is_flagged,
                    "flag_reason": phone_record.flag_reason,
                    "risk_score": phone_record.risk_score,
                    "info": phone_record.info,
                    "origin": phone_record.origin,
                    "last_checked": phone_record.last_checked,
                    "created_at": phone_record.created_at
                }

            # --------------------------
            # Not found: Create new record
            # --------------------------
            risk_score = 20
            flag_reason = ""
            is_flagged = False

          
            if not cleaned_number.startswith("+84"):
                is_flagged = True
                flag_reason = "Số điện thoại nước ngoài"
                risk_score = 60

            if re.match(r"^(\+8490|\+8486)", cleaned_number):
                risk_score = max(risk_score, 70)
                is_flagged = True
                flag_reason = "Số có dấu hiệu lừa đảo trong số máy"

            # Create phone record
            phone_record = PhoneNumber(
                number=cleaned_number,
                info=f"Lần đầu gọi cho {user_id}" if user_id else "First seen (system check)",
                origin="auto_check",
                is_flagged=is_flagged,
                flag_reason=flag_reason,
                risk_score=risk_score,
                created_at=datetime.utcnow(),
                last_checked=datetime.utcnow()
            )
            self.db.add(phone_record)
            self.db.commit()
            self.db.refresh(phone_record)

            logger.info(f"DEBUG: user_id={user_id}, is_flagged={phone_record.is_flagged}, risk={phone_record.risk_score}")
            
            if user_id: 
                if phone_record.is_flagged:
                    self._create_alerts_for_high_risk_phone(user_id, phone_record)
            
                if phone_record.risk_score >= 60 and phone_record <= 80:
                    self._create_family_only_alerts(user_id, phone_record)

            return {
                "found": False,
                "is_flagged": phone_record.is_flagged,
                "flag_reason": phone_record.flag_reason,
                "risk_score": phone_record.risk_score,
                "message": "Số điện thoại chưa có trong cơ sở dữ liệu, đã được thêm mới để theo dõi."
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error checking phone number {phone_number}: {str(e)}")
            raise
    
    def _create_alerts_for_high_risk_phone(self, user_id: int, phone_record: PhoneNumber) -> None:
        """
        Create alerts for both the elderly user and their linked family members
        when a high-risk phone number is detected
        """
        try:
            alert_service = AlertService(self.db)
            
            # Create alert for the elderly user
            user_alert = alert_service.create_phone_based_alert(
                user_id=user_id,
                phone_number=phone_record.number,
                risk_score=phone_record.risk_score,
                flag_reason=phone_record.flag_reason
            )
            
            logger.info(f"Created alert {user_alert.id} for user {user_id} about high-risk phone {phone_record.number}")
            
            # Create alerts for linked family members
            self._create_family_member_alerts(user_id, phone_record, alert_service)
            
        except Exception as e:
            logger.error(f"Error creating alerts for high-risk phone {phone_record.number}: {str(e)}")
            # Don't raise here to avoid breaking the main phone check flow
    
    def _create_family_only_alerts(self, elderly_user_id: int, phone_record: PhoneNumber) -> None:
        """
        Create alerts ONLY for family members when a phone number with risk score 60-80
        is detected for elderly users. This provides family notification without alarming the elderly user.
        """
        try:
            alert_service = AlertService(self.db)
            
            # Create alerts for linked family members only
            self._create_family_member_alerts_family_only(elderly_user_id, phone_record, alert_service)
            
            logger.info(f"Created family-only alerts for phone {phone_record.number} with risk score {phone_record.risk_score}")
            
        except Exception as e:
            logger.error(f"Error creating family-only alerts for phone {phone_record.number}: {str(e)}")
            # Don't raise here to avoid breaking the main phone check flow
    
    def _create_family_member_alerts_family_only(self, elderly_user_id: int, phone_record: PhoneNumber, alert_service: AlertService) -> None:
        """
        Create family-only alerts for family members linked to the elderly user
        These alerts are not shown to the elderly user to avoid unnecessary alarm
        """
        try:
            # Get family members who should be notified
            family_members = self.db.query(FamilyMember).filter(
                and_(
                    FamilyMember.user_id == elderly_user_id,
                    FamilyMember.notify_on_alert == True,
                    FamilyMember.linked_user_id.isnot(None)
                )
            ).all()
            
            for family_member in family_members:
                try:
                    # Create family-only alert for family member
                    family_alert = alert_service.create_family_only_alert(
                        elderly_user_id=elderly_user_id,
                        family_member_id=family_member.linked_user_id,
                        phone_number=phone_record.number,
                        risk_score=phone_record.risk_score,
                        flag_reason=phone_record.flag_reason
                    )
                    
                    logger.info(f"Created family-only alert {family_alert.id} for user {family_member.linked_user_id}")
                    
                except Exception as e:
                    logger.error(f"Error creating family-only alert for family member {family_member.linked_user_id}: {str(e)}")
                    # Continue with other family members
                    continue
            
            logger.info(f"Created family-only alerts for {len(family_members)} family members about phone {phone_record.number}")
            
        except Exception as e:
            logger.error(f"Error creating family-only alerts: {str(e)}")
            # Don't raise here to avoid breaking the main flow
    
    def _create_family_member_alerts(self, elderly_user_id: int, phone_record: PhoneNumber, alert_service: AlertService) -> None:
        """
        Create alerts for family members linked to the elderly user
        """
        try:
            # Get family members who should be notified
            family_members = self.db.query(FamilyMember).filter(
                and_(
                    FamilyMember.user_id == elderly_user_id,
                    FamilyMember.notify_on_alert == True,
                    FamilyMember.linked_user_id.isnot(None)
                )
            ).all()
            
            for family_member in family_members:
                try:
                    # Create alert for family member
                    family_alert = alert_service.create_family_member_alert(
                        elderly_user_id=elderly_user_id,
                        family_member_id=family_member.linked_user_id,
                        phone_number=phone_record.number,
                        risk_score=phone_record.risk_score,
                        flag_reason=phone_record.flag_reason
                    )
                    
                    logger.info(f"Created family member alert {family_alert.id} for user {family_member.linked_user_id}")
                    
                except Exception as e:
                    logger.error(f"Error creating alert for family member {family_member.linked_user_id}: {str(e)}")
                    # Continue with other family members
                    continue
            
            logger.info(f"Created alerts for {len(family_members)} family members about high-risk phone {phone_record.number}")
            
        except Exception as e:
            logger.error(f"Error creating family member alerts: {str(e)}")
            # Don't raise here to avoid breaking the main flow
    
    def add_phone_number(self, phone_data: PhoneNumberCreate) -> PhoneNumber:
        """
        Add a new phone number to the database
        """
        try:
            cleaned_number = self._clean_phone_number(phone_data.number)
            
            # Check if phone number already exists
            existing_phone = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()
            
            if existing_phone:
                raise ValueError(f"Phone number {cleaned_number} already exists")
            
            phone_record = PhoneNumber(
                number=cleaned_number,
                country_code=phone_data.country_code,
                info=phone_data.info,
                origin=phone_data.origin,
                owner_id=phone_data.owner_id
            )
            
            self.db.add(phone_record)
            self.db.commit()
            self.db.refresh(phone_record)
            
            return phone_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding phone number: {str(e)}")
            raise
    
    def flag_phone_number(self, phone_number: str, flag_reason: str, risk_score: int = 50) -> PhoneNumber:
        """
        Flag a phone number as suspicious or scam
        """
        try:
            cleaned_number = self._clean_phone_number(phone_number)
            
            phone_record = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()
            
            if not phone_record:
                # Create new record if doesn't exist
                phone_record = PhoneNumber(
                    number=cleaned_number,
                    is_flagged=True,
                    flag_reason=flag_reason,
                    risk_score=risk_score
                )
                self.db.add(phone_record)
            else:
                # Update existing record
                phone_record.is_flagged = True
                phone_record.flag_reason = flag_reason
                phone_record.risk_score = risk_score
                phone_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(phone_record)
            
            return phone_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error flagging phone number: {str(e)}")
            raise
    
    def get_flagged_phones(self, limit: int = 100, offset: int = 0) -> List[PhoneNumber]:
        """
        Get all flagged phone numbers
        """
        try:
            return self.db.query(PhoneNumber).filter(
                PhoneNumber.is_flagged == True
            ).order_by(PhoneNumber.updated_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting flagged phones: {str(e)}")
            raise
    
    def get_phone_by_id(self, phone_id: int) -> Optional[PhoneNumber]:
        """
        Get phone number by ID
        """
        try:
            return self.db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
        except Exception as e:
            logger.error(f"Error getting phone by ID {phone_id}: {str(e)}")
            raise
    
    def update_phone_risk_score(self, phone_id: int, risk_score: int) -> PhoneNumber:
        """
        Update the risk score of a phone number
        """
        try:
            phone_record = self.get_phone_by_id(phone_id)
            if not phone_record:
                raise ValueError(f"Số điện thoại với {phone_id} khônh được tìm thấy")
            
            phone_record.risk_score = risk_score
            phone_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(phone_record)
            
            return phone_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating phone risk score: {str(e)}")
            raise
    
    def search_phones(self, query: str, limit: int = 50) -> List[PhoneNumber]:
        """
        Search phone numbers by number, info, or origin
        """
        try:
            return self.db.query(PhoneNumber).filter(
                or_(
                    PhoneNumber.number.contains(query),
                    PhoneNumber.info.contains(query),
                    PhoneNumber.origin.contains(query)
                )
            ).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching phones: {str(e)}")
            raise
    
    def get_user_phones(self, user_id: int) -> List[PhoneNumber]:
        """
        Get all phone numbers associated with a user
        """
        try:
            return self.db.query(PhoneNumber).filter(
                PhoneNumber.owner_id == user_id
            ).all()
            
        except Exception as e:
            logger.error(f"Error getting user phones: {str(e)}")
            raise
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """
        Clean and normalize a Vietnamese phone number to international format (+84...).
        - Accepts numbers in format: +84..., or 0(9|3|7|8|5|2)...
        - Removes spaces, dashes, dots, and other non-digit characters (except + at start)
        """
        import re
        
        # Remove all non-digit characters except leading +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # If already starts with +84 → keep it
        if cleaned.startswith("+84"):
            return cleaned
        
        # If starts with 0 → convert to +84
        if cleaned.startswith("0"):
            return f"+84{cleaned[1:]}"
        
        # If starts with '84' but missing '+' at front
        if cleaned.startswith("84"):
            return f"+{cleaned}"
        
        # Final fallback: return as-is if we don't know the format
        return cleaned