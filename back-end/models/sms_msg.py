from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class SMSLog(Base):
    __tablename__ = "sms_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    message_body = Column(Text, nullable=False)
    sender = Column(String(20), nullable=False, index=True)
    is_flagged = Column(Boolean, default=False, index=True)
    flag_reason = Column(String(255), nullable=True)
    risk_score = Column(Integer, default=0)  # Risk score from 0-100
    message_type = Column(String(50), nullable=True)  # "incoming", "outgoing"
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_id = Column(Integer, ForeignKey("phone_numbers.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sms_logs")
    phone = relationship("PhoneNumber", back_populates="sms_logs")
    scan_requests = relationship("ScanRequest", back_populates="sms", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="reported_sms", cascade="all, delete-orphan")
