from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    linked_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    relation_type = Column(String(100), nullable=True)  # "spouse", "child", "parent", "sibling"
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    notify_on_alert = Column(Boolean, default=True)
    is_primary_contact = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="family_members")
    linked_user = relationship("User", foreign_keys=[linked_user_id])
    alerts = relationship("Alert", back_populates="family_member", cascade="all, delete-orphan")

