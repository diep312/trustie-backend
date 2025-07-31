from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.phone_number import PhoneNumber
from ..models.user import User
from ..models.alert import Alert
from ..models.family import FamilyMember
from ..schemas import PhoneNumberCreate, PhoneNumber as PhoneNumberSchema
import logging

logger = logging.getLogger(__name__)

class PhoneService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_phone_number(self, phone_number: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Check if a phone number is flagged in the database
        Returns detailed information about the phone number
        """
        try:
            # Clean the phone number (remove spaces, dashes, etc.)
            cleaned_number = self._clean_phone_number(phone_number)
            
            # Search for the phone number in the database
            phone_record = self.db.query(PhoneNumber).filter(
                PhoneNumber.number == cleaned_number
            ).first()
            
            if phone_record:
                # Update last_checked timestamp
                phone_record.last_checked = datetime.utcnow()
                self.db.commit()
                
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
            else:
                return {
                    "found": False,
                    "is_flagged": False,
                    "risk_score": 0,
                    "message": "Số điện thoại không được tìm thấy trong cơ sở dữ liệu."
                }
                
        except Exception as e:
            logger.error(f"Error checking phone number {phone_number}: {str(e)}")
            raise
    
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
        Clean phone number by removing spaces, dashes, and other non-digit characters
        """
        import re
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        return cleaned 