from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Screenshot(Base):
    __tablename__ = "screenshots"
    
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(500), nullable=False)
    image_size = Column(Integer, nullable=True)  # Size in bytes
    image_format = Column(String(10), nullable=True)  # "jpg", "png", etc.
    description = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False, index=True)
    ocr_text = Column(Text, nullable=True)  # Extracted text from OCR
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="screenshots")
    scan_requests = relationship("ScanRequest", back_populates="screenshot", cascade="all, delete-orphan")


