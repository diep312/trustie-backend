from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class SourceTypeEnum(str, Enum):
    PHONE = "phone"
    SCREENSHOT = "screenshot"
    WEBSITE = "website"
    SMS = "sms"

class ResultLabelEnum(str, Enum):
    SAFE = "safe"
    SCAM = "scam"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"

class AlertTypeEnum(str, Enum):
    SCAM_DETECTED = "scam_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    HIGH_RISK = "high_risk"
    URGENT = "urgent"

class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Base schemas
class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    device_id: str
    is_elderly: bool = False

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Phone Number schemas
class PhoneNumberBase(BaseModel):
    number: str
    country_code: Optional[str] = None
    info: Optional[str] = None
    origin: Optional[str] = None

class PhoneNumberCreate(PhoneNumberBase):
    owner_id: Optional[int] = None

class PhoneNumber(PhoneNumberBase):
    id: int
    is_flagged: bool
    flag_reason: Optional[str] = None
    risk_score: int
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True

# SMS schemas
class SMSLogBase(BaseModel):
    message_body: str
    sender: str
    message_type: Optional[str] = None

class SMSLogCreate(SMSLogBase):
    user_id: int
    phone_id: Optional[int] = None

class SMSLog(SMSLogBase):
    id: int
    is_flagged: bool
    flag_reason: Optional[str] = None
    risk_score: int
    timestamp: datetime
    created_at: datetime
    user_id: int
    phone_id: Optional[int] = None

    class Config:
        from_attributes = True

# Website schemas
class WebsiteBase(BaseModel):
    domain: str
    url: Optional[str] = None
    description: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    pass

class Website(WebsiteBase):
    id: int
    trust_worthy_point: float
    risk_score: int
    is_flagged: bool
    flag_reason: Optional[str] = None
    ssl_valid: Optional[bool] = None
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Scan Request schemas
class ScanRequestBase(BaseModel):
    source_from: str
    source_type: SourceTypeEnum
    priority: str = "medium"
    notes: Optional[str] = None

class ScanRequestCreate(ScanRequestBase):
    user_id: int
    screenshot_id: Optional[int] = None
    phone_id: Optional[int] = None
    website_id: Optional[int] = None
    sms_id: Optional[int] = None

class ScanRequest(ScanRequestBase):
    id: int
    status: str
    timestamp: datetime
    completed_at: Optional[datetime] = None
    user_id: int
    screenshot_id: Optional[int] = None
    phone_id: Optional[int] = None
    website_id: Optional[int] = None
    sms_id: Optional[int] = None

    class Config:
        from_attributes = True

# Scan Result schemas
class ScamDetectionResultBase(BaseModel):
    source_type: SourceTypeEnum
    source_id: int
    result_label: ResultLabelEnum
    confidence_score: float
    detection_method: Optional[str] = None
    analysis_details: Optional[str] = None

class ScamDetectionResultCreate(ScamDetectionResultBase):
    scan_request_id: Optional[int] = None

class ScamDetectionResult(ScamDetectionResultBase):
    id: int
    risk_score: int
    ai_model_version: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    scan_request_id: Optional[int] = None

    class Config:
        from_attributes = True

# Alert schemas
class AlertBase(BaseModel):
    alert_type: AlertTypeEnum
    severity: SeverityEnum = SeverityEnum.MEDIUM
    message: str

class AlertCreate(AlertBase):
    user_id: int
    family_member_id: Optional[int] = None
    detection_result_id: int

class Alert(AlertBase):
    id: int
    user_id: int
    family_member_id: Optional[int] = None
    detection_result_id: int
    is_read: bool
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Family Member schemas
class FamilyMemberBase(BaseModel):
    name: str
    relationship: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    notify_on_alert: bool = True
    is_primary_contact: bool = False

class FamilyMemberCreate(FamilyMemberBase):
    user_id: int
    linked_user_id: Optional[int] = None

class FamilyMember(FamilyMemberBase):
    id: int
    user_id: int
    linked_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Report schemas
class ReportBase(BaseModel):
    reason: str
    report_type: str
    priority: str = "medium"

class ReportCreate(ReportBase):
    user_id: int
    reported_phone_id: Optional[int] = None
    reported_website_id: Optional[int] = None
    reported_sms_id: Optional[int] = None

class Report(ReportBase):
    id: int
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    user_id: int
    reported_phone_id: Optional[int] = None
    reported_website_id: Optional[int] = None
    reported_sms_id: Optional[int] = None

    class Config:
        from_attributes = True

# Screenshot schemas
class ScreenshotBase(BaseModel):
    image_path: str
    description: Optional[str] = None

class ScreenshotCreate(ScreenshotBase):
    user_id: int

class Screenshot(ScreenshotBase):
    id: int
    image_size: Optional[int] = None
    image_format: Optional[str] = None
    is_processed: bool
    ocr_text: Optional[str] = None
    timestamp: datetime
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# Feedback schemas
class FeedbackBase(BaseModel):
    feedback_type: str
    info: str
    rating: Optional[int] = None

class FeedbackCreate(FeedbackBase):
    user_id: int

class Feedback(FeedbackBase):
    id: int
    status: str
    admin_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True 