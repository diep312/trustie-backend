# Trustie Backend API Documentation

This API provides comprehensive phone scam detection and alerting functionality for protecting elderly users from phone scams.

## Base URL
```
http://localhost:8000
```

## API Endpoints

### Phone Number Management

#### Check Phone Number
```http
POST /phone/check
```
Check if a phone number is flagged in the database.

**Request Body:**
```json
{
  "phone_number": "+18005551234",
  "user_id": 1
}
```

**Response:**
```json
{
  "found": true,
  "is_flagged": true,
  "flag_reason": "Known scam number",
  "risk_score": 85,
  "info": "IRS scam caller",
  "origin": "User report",
  "last_checked": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-10T08:00:00Z",
  "message": null
}
```

#### Flag Phone Number
```http
POST /phone/flag
```
Flag a phone number as suspicious or scam.

**Request Body:**
```json
{
  "phone_number": "+18005551234",
  "flag_reason": "IRS scam attempt",
  "risk_score": 90
}
```

#### Get Flagged Phones
```http
GET /phone/flagged?limit=100&offset=0
```
Get all flagged phone numbers.

#### Search Phones
```http
POST /phone/search
```
Search phone numbers by number, info, or origin.

**Request Body:**
```json
{
  "query": "IRS",
  "limit": 50
}
```

#### Check and Create Alert
```http
POST /phone/check-and-alert
```
Check phone number and create alert if flagged.

**Request Body:**
```json
{
  "phone_number": "+18005551234",
  "user_id": 1
}
```

### Scam Detection

#### Comprehensive Scam Detection
```http
POST /scam-detection/detect
```
Perform comprehensive scam detection including AI analysis and alert creation.

**Request Body:**
```json
{
  "phone_number": "+18005551234",
  "user_id": 1,
  "context": "Caller says my social security account is suspended"
}
```

**Response:**
```json
{
  "phone_check": {
    "found": true,
    "is_flagged": true,
    "risk_score": 85
  },
  "ai_analysis": {
    "result_label": "scam",
    "confidence_score": 92,
    "risk_score": 90,
    "risk_factors": ["Toll-free number", "Suspicious context"],
    "reason": "Toll-free number, Suspicious context",
    "detection_method": "heuristic_analysis",
    "processing_time": 0.1
  },
  "detection_result_id": 123,
  "scan_request_id": 456,
  "alert_created": true,
  "alert_id": 789,
  "recommendation": "BLOCK: This number has been identified as a scam. Do not answer or call back."
}
```

#### Risk Assessment
```http
GET /scam-detection/risk-assessment/{phone_number}?context=urgent call
```
Get detailed risk assessment without creating alerts.

**Response:**
```json
{
  "phone_number": "+18005551234",
  "database_check": {
    "found": true,
    "is_flagged": true,
    "risk_score": 85
  },
  "ai_analysis": {
    "result_label": "scam",
    "confidence_score": 92,
    "risk_score": 90
  },
  "overall_risk_score": 90,
  "risk_level": "CRITICAL",
  "recommendation": "BLOCK: This number has been identified as a scam."
}
```

#### Detection History
```http
GET /scam-detection/history/{user_id}?limit=50
```
Get user's scam detection history.

#### Detection Statistics
```http
GET /scam-detection/stats/{user_id}
```
Get scam detection statistics for a user.

#### Bulk Phone Check
```http
POST /scam-detection/bulk-check?user_id=1
```
Check multiple phone numbers at once.

**Request Body:**
```json
[
  "+18005551234",
  "+12345678901",
  "+447911123456"
]
```

### Alert Management

#### Get User Alerts
```http
GET /alerts/user/{user_id}?limit=50&offset=0&unread_only=false
```
Get alerts for a specific user.

#### Get Unread Alert Count
```http
GET /alerts/user/{user_id}/unread-count
```
Get count of unread alerts for a user.

#### Mark Alert as Read
```http
PUT /alerts/{alert_id}/read?user_id=1
```
Mark an alert as read.

#### Acknowledge Alert
```http
PUT /alerts/{alert_id}/acknowledge?user_id=1
```
Acknowledge an alert.

#### Delete Alert
```http
DELETE /alerts/{alert_id}?user_id=1
```
Delete an alert.

#### Get Alerts by Severity
```http
GET /alerts/user/{user_id}/severity/{severity}
```
Get alerts by severity level (low, medium, high, critical).

#### Get Critical Alerts
```http
GET /alerts/user/{user_id}/critical
```
Get critical alerts for a user.

#### Mark All Alerts as Read
```http
PUT /alerts/user/{user_id}/mark-all-read
```
Mark all alerts for a user as read.

## Data Models

### Phone Number
```json
{
  "id": 1,
  "number": "+18005551234",
  "country_code": "+1",
  "info": "IRS scam caller",
  "origin": "User report",
  "is_flagged": true,
  "flag_reason": "Known scam number",
  "risk_score": 85,
  "last_checked": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "owner_id": 1
}
```

### Alert
```json
{
  "id": 1,
  "user_id": 1,
  "alert_type": "scam_detected",
  "severity": "high",
  "message": "Potential scam detected from phone number +18005551234. Risk score: 85/100",
  "is_read": false,
  "is_acknowledged": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Phone number +18005551234 already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Phone number not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Usage Examples

### Python Example
```python
import requests

# Check a phone number
response = requests.post("http://localhost:8000/phone/check", json={
    "phone_number": "+18005551234",
    "user_id": 1
})

if response.status_code == 200:
    result = response.json()
    if result["is_flagged"]:
        print(f"WARNING: {result['flag_reason']}")
        print(f"Risk Score: {result['risk_score']}")
```

### JavaScript Example
```javascript
// Check a phone number
const response = await fetch('http://localhost:8000/phone/check', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        phone_number: '+18005551234',
        user_id: 1
    })
});

const result = await response.json();
if (result.is_flagged) {
    console.log(`WARNING: ${result.flag_reason}`);
    console.log(`Risk Score: ${result.risk_score}`);
}
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
uvicorn main:app --reload
```

3. Access the API documentation:
```
http://localhost:8000/docs
```

## Testing

Run the test script to verify functionality:
```bash
python test_api.py
```

## Security Considerations

- All endpoints should be protected with authentication in production
- Phone numbers are cleaned and validated before processing
- Risk scores are calculated based on multiple factors
- Alerts are created with appropriate severity levels
- Family member notifications are handled securely

## Integration with AI Engine

The scam detection service integrates with the AI engine in the `ai-engine/` directory for:
- Phone number pattern analysis
- Context-based risk assessment
- Machine learning model predictions
- Real-time threat detection 