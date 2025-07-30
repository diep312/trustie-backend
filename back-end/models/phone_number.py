from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, nullable=False, index=True)
    country_code = Column(String(5), nullable=True)
    info = Column(Text, nullable=True)  # Additional information about the number
    origin = Column(String(100), nullable=True)  # Where this number was found
    is_flagged = Column(Boolean, default=False, index=True)
    flag_reason = Column(String(255), nullable=True)  # Reason for flagging
    risk_score = Column(Integer, default=0)  # Risk score from 0-100
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="phones")
    sms_logs = relationship("SMSLog", back_populates="phone", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="reported_phone", cascade="all, delete-orphan")
    scan_requests = relationship("ScanRequest", back_populates="phone", cascade="all, delete-orphan")
