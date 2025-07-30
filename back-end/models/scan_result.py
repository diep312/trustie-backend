import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base

class ScamDetectionResult(Base):
    __tablename__ = "scam_detection_results"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(SQLEnum("phone", "screenshot", "website", "sms", name="source_type_enum"), nullable=False)
    source_id = Column(Integer, nullable=False)  # FK is dynamic based on source_type
    result_label = Column(SQLEnum("safe", "scam", "suspicious", "unknown", name="result_label_enum"), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_score = Column(Integer, default=0)  # 0-100 risk score
    detection_method = Column(String(100), nullable=True)  # "ai_model", "rule_based", "manual"
    analysis_details = Column(Text, nullable=True)  # Detailed analysis results
    ai_model_version = Column(String(50), nullable=True)
    processing_time = Column(Float, nullable=True)  # Time taken to process in seconds
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Foreign key to scan request
    scan_request_id = Column(Integer, ForeignKey("scan_requests.id"), nullable=True)
    
    # Relationships
    scan_request = relationship("ScanRequest", back_populates="scan_results")
    alerts = relationship("Alert", back_populates="detection_result", cascade="all, delete-orphan")
