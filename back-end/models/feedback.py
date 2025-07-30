from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_type = Column(SQLEnum("bug_report", "feature_request", "general", "accuracy", name="feedback_type_enum"), nullable=False)
    info = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    status = Column(SQLEnum("open", "in_progress", "resolved", "closed", name="feedback_status_enum"), default="open")
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    user = relationship("User", back_populates="feedbacks") 