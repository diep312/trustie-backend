# Trustie Backend - Data Models Documentation

## Overview
This document describes the data models for the Trustie anti-scammer detection system. The models are designed to handle phone numbers, SMS messages, websites, screenshots, and various detection results with comprehensive tracking and alerting capabilities.

## Database Schema

### Core Models

#### 1. User
**Table**: `users`
**Purpose**: Represents application users, particularly elderly users who need protection from scams.

**Key Fields**:
- `id`: Primary key
- `name`: User's full name
- `email`: Optional email address
- `device_id`: Unique device identifier (required)
- `is_elderly`: Boolean flag for elderly users
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

**Relationships**:
- Has many PhoneNumbers
- Has many SMSLogs
- Has many Screenshots
- Has many Alerts
- Has many Feedbacks
- Has many Reports
- Has many FamilyMembers
- Has many ScanRequests

#### 2. PhoneNumber
**Table**: `phone_numbers`
**Purpose**: Stores phone numbers for scam detection and tracking.

**Key Fields**:
- `id`: Primary key
- `number`: Phone number (unique, indexed)
- `country_code`: Country code (e.g., "+1")
- `info`: Additional information about the number
- `origin`: Where this number was found
- `is_flagged`: Whether flagged as suspicious
- `flag_reason`: Reason for flagging
- `risk_score`: Risk score (0-100)
- `last_checked`: Last verification timestamp
- `owner_id`: Associated user (optional)

**Relationships**:
- Belongs to User (owner)
- Has many SMSLogs
- Has many Reports
- Has many ScanRequests

#### 3. SMSLog
**Table**: `sms_logs`
**Purpose**: Tracks SMS messages for scam detection.

**Key Fields**:
- `id`: Primary key
- `message_body`: SMS content
- `sender`: Sender phone number
- `is_flagged`: Whether flagged as suspicious
- `flag_reason`: Reason for flagging
- `risk_score`: Risk score (0-100)
- `message_type`: "incoming" or "outgoing"
- `timestamp`: Message timestamp
- `user_id`: Associated user
- `phone_id`: Associated phone number (optional)

**Relationships**:
- Belongs to User
- Belongs to PhoneNumber (optional)
- Has many ScanRequests
- Has many Reports

#### 4. Website
**Table**: `websites`
**Purpose**: Stores website information for scam detection.

**Key Fields**:
- `id`: Primary key
- `domain`: Website domain (unique, indexed)
- `url`: Full URL
- `description`: Website description
- `trust_worthy_point`: Trust score (0.0-1.0)
- `risk_score`: Risk score (0-100)
- `is_flagged`: Whether flagged as suspicious
- `flag_reason`: Reason for flagging
- `ssl_valid`: SSL certificate validity
- `last_checked`: Last verification timestamp

**Relationships**:
- Has many ScanRequests
- Has many Reports

### Detection Models

#### 5. ScanRequest
**Table**: `scan_requests`
**Purpose**: Tracks scan requests for various content types.

**Key Fields**:
- `id`: Primary key
- `source_from`: Request source ("manual", "automatic", "scheduled")
- `source_type`: Content type ("phone", "screenshot", "website", "sms")
- `status`: Request status ("pending", "processing", "completed", "failed")
- `priority`: Priority level ("low", "medium", "high", "urgent")
- `notes`: Additional notes
- `timestamp`: Request timestamp
- `completed_at`: Completion timestamp
- `user_id`: Requesting user

**Foreign Keys** (only one should be set based on source_type):
- `screenshot_id`: Associated screenshot
- `phone_id`: Associated phone number
- `website_id`: Associated website
- `sms_id`: Associated SMS

**Relationships**:
- Belongs to User
- Belongs to Screenshot (optional)
- Belongs to PhoneNumber (optional)
- Belongs to Website (optional)
- Belongs to SMSLog (optional)
- Has many ScamDetectionResults

#### 6. ScamDetectionResult
**Table**: `scam_detection_results`
**Purpose**: Stores AI detection results and analysis.

**Key Fields**:
- `id`: Primary key
- `source_type`: Content type analyzed
- `source_id`: ID of the analyzed content
- `result_label`: Detection result ("safe", "scam", "suspicious", "unknown")
- `confidence_score`: AI confidence (0.0-1.0)
- `risk_score`: Risk score (0-100)
- `detection_method`: Detection method used
- `analysis_details`: Detailed analysis results
- `ai_model_version`: AI model version used
- `processing_time`: Processing time in seconds
- `scan_request_id`: Associated scan request

**Relationships**:
- Belongs to ScanRequest
- Has many Alerts

### Alerting Models

#### 7. Alert
**Table**: `alerts`
**Purpose**: Manages alerts for detected scams and suspicious activities.

**Key Fields**:
- `id`: Primary key
- `alert_type`: Alert type ("scam_detected", "suspicious_activity", "high_risk", "urgent")
- `severity`: Severity level ("low", "medium", "high", "critical")
- `message`: Alert message
- `is_read`: Read status
- `is_acknowledged`: Acknowledgment status
- `acknowledged_at`: Acknowledgment timestamp
- `acknowledged_by`: User who acknowledged
- `user_id`: Alert recipient
- `family_member_id`: Associated family member (optional)
- `detection_result_id`: Associated detection result

**Relationships**:
- Belongs to User (recipient)
- Belongs to FamilyMember (optional)
- Belongs to ScamDetectionResult
- Belongs to User (acknowledger)

#### 8. FamilyMember
**Table**: `family_members`
**Purpose**: Manages family member relationships for alert notifications.

**Key Fields**:
- `id`: Primary key
- `name`: Family member name
- `relationship`: Relationship type ("spouse", "child", "parent", "sibling")
- `phone_number`: Contact phone number
- `email`: Contact email
- `notify_on_alert`: Whether to notify on alerts
- `is_primary_contact`: Primary contact flag
- `user_id`: Associated user
- `linked_user_id`: Linked user account (optional)

**Relationships**:
- Belongs to User
- Belongs to User (linked user)
- Has many Alerts

### Support Models

#### 9. Screenshot
**Table**: `screenshots`
**Purpose**: Stores screenshots for OCR analysis and scam detection.

**Key Fields**:
- `id`: Primary key
- `image_path`: File path to image
- `image_size`: File size in bytes
- `image_format`: Image format ("jpg", "png", etc.)
- `description`: Screenshot description
- `is_processed`: Processing status
- `ocr_text`: Extracted text from OCR
- `timestamp`: Screenshot timestamp
- `user_id`: Associated user

**Relationships**:
- Belongs to User
- Has many ScanRequests

#### 10. Report
**Table**: `reports`
**Purpose**: Handles user reports of suspicious content.

**Key Fields**:
- `id`: Primary key
- `reason`: Report reason
- `report_type`: Content type reported ("phone", "website", "sms", "general")
- `status`: Report status ("pending", "reviewed", "resolved", "dismissed")
- `priority`: Priority level
- `admin_notes`: Admin notes
- `user_id`: Reporting user
- `reported_phone_id`: Reported phone number (optional)
- `reported_website_id`: Reported website (optional)
- `reported_sms_id`: Reported SMS (optional)

**Relationships**:
- Belongs to User (reporter)
- Belongs to PhoneNumber (reported)
- Belongs to Website (reported)
- Belongs to SMSLog (reported)

#### 11. Feedback
**Table**: `feedbacks`
**Purpose**: Collects user feedback about the system.

**Key Fields**:
- `id`: Primary key
- `feedback_type`: Feedback type ("bug_report", "feature_request", "general", "accuracy")
- `info`: Feedback content
- `rating`: User rating (1-5)
- `status`: Feedback status ("open", "in_progress", "resolved", "closed")
- `admin_response`: Admin response
- `user_id`: Feedback author

**Relationships**:
- Belongs to User

## Database Design Principles

### 1. Comprehensive Tracking
- All models include timestamps for audit trails
- Risk scores and confidence levels for quantitative analysis
- Detailed flagging reasons for transparency

### 2. Flexible Relationships
- Optional foreign keys allow for various content types
- Many-to-many relationships through intermediate tables
- Cascade deletes for data integrity

### 3. Scalability
- Proper indexing on frequently queried fields
- Enum types for consistent data values
- Efficient relationship loading with back_populates

### 4. Security
- User isolation through foreign key relationships
- Audit trails for all critical operations
- Status tracking for workflow management

## Usage Examples

### Creating a User
```python
from models import User
from database import SessionLocal

db = SessionLocal()
user = User(
    name="John Doe",
    email="john@example.com",
    device_id="device_123",
    is_elderly=True
)
db.add(user)
db.commit()
```

### Scanning a Phone Number
```python
from models import ScanRequest, PhoneNumber
from schemas import SourceTypeEnum

# Create scan request
scan_request = ScanRequest(
    source_from="manual",
    source_type=SourceTypeEnum.PHONE,
    user_id=user.id,
    phone_id=phone_number.id,
    priority="high"
)
db.add(scan_request)
db.commit()
```

### Creating an Alert
```python
from models import Alert
from schemas import AlertTypeEnum, SeverityEnum

alert = Alert(
    alert_type=AlertTypeEnum.SCAM_DETECTED,
    severity=SeverityEnum.HIGH,
    message="Suspicious phone number detected",
    user_id=user.id,
    detection_result_id=result.id
)
db.add(alert)
db.commit()
```

## Migration Notes

When migrating from the old schema:
1. Add new columns with default values
2. Update existing relationships
3. Migrate enum values to new format
4. Add missing indexes for performance

## Performance Considerations

1. **Indexes**: All primary keys and frequently queried fields are indexed
2. **Cascade Deletes**: Properly configured to maintain referential integrity
3. **Lazy Loading**: Relationships are loaded on demand to reduce memory usage
4. **Batch Operations**: Use bulk operations for large datasets

## Security Considerations

1. **Input Validation**: All inputs are validated through Pydantic schemas
2. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
3. **Data Isolation**: Users can only access their own data
4. **Audit Trails**: All critical operations are timestamped 