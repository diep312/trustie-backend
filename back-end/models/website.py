from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    trust_worthy_point = Column(Float, default=0.0)  # Trust score from 0.0 to 1.0
    risk_score = Column(Integer, default=0)  # Risk score from 0-100
    is_flagged = Column(Boolean, default=False, index=True)
    flag_reason = Column(String(255), nullable=True)
    ssl_valid = Column(Boolean, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scan_requests = relationship("ScanRequest", back_populates="website", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="reported_website", cascade="all, delete-orphan")