import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base

class ScanRequest(Base):
    __tablename__ = "scan_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    source_from = Column(String(100), nullable=False)  # "manual", "automatic", "scheduled"
    source_type = Column(SQLEnum("phone", "screenshot", "website", "sms", name="source_type_enum"), nullable=False)
    status = Column(SQLEnum("pending", "processing", "completed", "failed", name="scan_status_enum"), default="pending")
    priority = Column(SQLEnum("low", "medium", "high", "urgent", name="priority_enum"), default="medium")
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Foreign keys - only one should be set based on source_type
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    screenshot_id = Column(Integer, ForeignKey("screenshots.id"), nullable=True)
    phone_id = Column(Integer, ForeignKey("phone_numbers.id"), nullable=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=True)
    sms_id = Column(Integer, ForeignKey("sms_logs.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="scan_requests")
    screenshot = relationship("Screenshot", back_populates="scan_requests")
    phone = relationship("PhoneNumber", back_populates="scan_requests")
    website = relationship("Website", back_populates="scan_requests")
    sms = relationship("SMSLog", back_populates="scan_requests")
    scan_results = relationship("ScamDetectionResult", back_populates="scan_request", cascade="all, delete-orphan")