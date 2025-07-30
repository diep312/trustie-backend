from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    reason = Column(Text, nullable=False)
    report_type = Column(SQLEnum("phone", "website", "sms", "general", name="report_type_enum"), nullable=False)
    status = Column(SQLEnum("pending", "reviewed", "resolved", "dismissed", name="report_status_enum"), default="pending")
    priority = Column(SQLEnum("low", "medium", "high", "urgent", name="priority_enum"), default="medium")
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reported_phone_id = Column(Integer, ForeignKey('phone_numbers.id'), nullable=True)
    reported_website_id = Column(Integer, ForeignKey('websites.id'), nullable=True)
    reported_sms_id = Column(Integer, ForeignKey('sms_logs.id'), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    reported_phone = relationship("PhoneNumber", back_populates="reports")
    reported_website = relationship("Website", back_populates="reports")
    reported_sms = relationship("SMSLog", back_populates="reports")