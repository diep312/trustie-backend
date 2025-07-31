import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    detection_result_id = Column(Integer, ForeignKey("scam_detection_results.id"), nullable=False)
    
    alert_type = Column(SQLEnum("scam_detected", "suspicious_activity", "high_risk", "urgent", name="alert_type_enum"), nullable=False)
    severity = Column(SQLEnum("low", "medium", "high", "critical", name="severity_enum"), default="medium")
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])
    family_member = relationship("FamilyMember", back_populates="alerts")
    detection_result = relationship("ScamDetectionResult", back_populates="alerts")
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])
