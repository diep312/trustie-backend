from .base import Base
from .user import User
from .phone_number import PhoneNumber
from .sms_msg import SMSLog
from .website import Website
from .scan import ScanRequest
from .scan_result import ScamDetectionResult
from .alert import Alert
from .family import FamilyMember
from .feedback import Feedback
from .report import Report
from .screenshot import Screenshot

# Export all models for easy importing
__all__ = [
    "Base",
    "User", 
    "PhoneNumber",
    "SMSLog",
    "Website",
    "ScanRequest",
    "ScamDetectionResult",
    "Alert",
    "FamilyMember",
    "Feedback",
    "Report",
    "Screenshot"
]
