from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    device_id = Column(String(255), unique=True, nullable=False)
    is_elderly = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    phones = relationship("PhoneNumber", back_populates="owner", cascade="all, delete-orphan")
    sms_logs = relationship("SMSLog", back_populates="user", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan", foreign_keys="Alert.user_id")    
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    family_members = relationship("FamilyMember", foreign_keys="FamilyMember.user_id", back_populates="user", cascade="all, delete-orphan")
    scan_requests = relationship("ScanRequest", back_populates="user", cascade="all, delete-orphan")
