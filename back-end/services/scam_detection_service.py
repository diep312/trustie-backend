from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from .phone_service import PhoneService
from .alert_service import AlertService
from ..models.scan_result import ScamDetectionResult
from ..models.scan import ScanRequest
from ..schemas import SourceTypeEnum, ResultLabelEnum
import logging

logger = logging.getLogger(__name__)

class ScamDetectionService:
    def __init__(self, db: Session):
        self.db = db
        self.phone_service = PhoneService(db)
        self.alert_service = AlertService(db)
    
    def detect_scam_from_phone(self, phone_number: str, user_id: int, 
                              context: str = None) -> Dict[str, Any]:
        """
        Comprehensive scam detection for phone numbers
        This combines database lookup, AI analysis, and alert creation
        """
        try:
            # Step 1: Check if phone number is already flagged in database
            phone_check = self.phone_service.check_phone_number(phone_number, user_id)
            
            # Step 2: Create scan request for tracking
            scan_request = self._create_scan_request(
                user_id=user_id,
                source_type=SourceTypeEnum.PHONE,
                source_from=phone_number
            )
            
            # Step 3: Perform AI analysis (placeholder for now)
            ai_analysis = self._perform_ai_analysis(phone_number, context)
            
            # Step 4: Create detection result
            detection_result = self._create_detection_result(
                scan_request_id=scan_request.id,
                source_type=SourceTypeEnum.PHONE,
                source_id=phone_check.get("phone_id", 0),
                ai_analysis=ai_analysis
            )
            
            # Step 5: Update phone record if needed
            if phone_check["found"] and phone_check["is_flagged"]:
                # Phone is already flagged, update risk score if AI analysis suggests higher risk
                if ai_analysis["risk_score"] > phone_check["risk_score"]:
                    self.phone_service.update_phone_risk_score(
                        phone_check["phone_id"], 
                        ai_analysis["risk_score"]
                    )
                    phone_check["risk_score"] = ai_analysis["risk_score"]
            else:
                # Phone not in database, add it if AI analysis flags it
                if ai_analysis["result_label"] in [ResultLabelEnum.SCAM, ResultLabelEnum.SUSPICIOUS]:
                    phone_record = self.phone_service.flag_phone_number(
                        phone_number=phone_number,
                        flag_reason=ai_analysis["reason"],
                        risk_score=ai_analysis["risk_score"]
                    )
                    phone_check = {
                        "found": True,
                        "is_flagged": True,
                        "flag_reason": phone_record.flag_reason,
                        "risk_score": phone_record.risk_score,
                        "phone_id": phone_record.id
                    }
            
            # Step 6: Create alert if scam detected
            alert_created = False
            alert_id = None
            
            if (phone_check["is_flagged"] or 
                ai_analysis["result_label"] in [ResultLabelEnum.SCAM, ResultLabelEnum.SUSPICIOUS]):
                
                alert = self.alert_service.create_scam_alert(
                    user_id=user_id,
                    phone_number=phone_number,
                    risk_score=max(phone_check["risk_score"], ai_analysis["risk_score"]),
                    detection_result_id=detection_result.id,
                    message=f"Scam detected from {phone_number}. AI confidence: {ai_analysis['confidence_score']}%"
                )
                alert_created = True
                alert_id = alert.id
            
            # Step 7: Update scan request as completed
            scan_request.status = "completed"
            scan_request.completed_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "phone_check": phone_check,
                "ai_analysis": ai_analysis,
                "detection_result_id": detection_result.id,
                "scan_request_id": scan_request.id,
                "alert_created": alert_created,
                "alert_id": alert_id,
                "recommendation": self._get_recommendation(ai_analysis, phone_check)
            }
            
        except Exception as e:
            logger.error(f"Error in scam detection: {str(e)}")
            raise
    
    def _create_scan_request(self, user_id: int, source_type: SourceTypeEnum, 
                           source_from: str) -> ScanRequest:
        """
        Create a scan request for tracking
        """
        scan_request = ScanRequest(
            user_id=user_id,
            source_type=source_type,
            source_from=source_from,
            status="processing",
            timestamp=datetime.utcnow()
        )
        
        self.db.add(scan_request)
        self.db.commit()
        self.db.refresh(scan_request)
        
        return scan_request
    
    def _perform_ai_analysis(self, phone_number: str, context: str = None) -> Dict[str, Any]:
        """
        Perform AI analysis on phone number
        This is a placeholder - in real implementation, this would call your AI engine
        """
        # Placeholder AI analysis logic
        # In real implementation, this would call your AI engine from ai-engine/
        
        # Simple heuristic for demo purposes
        risk_factors = []
        risk_score = 0
        
        # Check for common scam patterns
        if phone_number.startswith("+1") and len(phone_number) == 12:
            # VN Number
            if any(pattern in phone_number for pattern in ["024", "028", "1900"]):
                risk_factors.append("Các đầu số điện thoại lừa đảo")
                risk_score += 20
        

        # Check for international numbers (higher risk)
        if phone_number.startswith("+") and not phone_number.startswith("+8"):
            risk_factors.append("Đầu số nước ngoài")
            risk_score += 25
        
        # Phân tích dựa trên ngữ cảnh nội dung
        if context:
            scam_keywords = ["urgent", "account", "suspended", "verify", "social security", "irs", "tax"]
            if any(keyword in context.lower() for keyword in scam_keywords):
                risk_factors.append("Suspicious context")
                risk_score += 40
        
        # Determine result label
        if risk_score >= 70:
            result_label = ResultLabelEnum.SCAM
        elif risk_score >= 40:
            result_label = ResultLabelEnum.SUSPICIOUS
        elif risk_score >= 20:
            result_label = ResultLabelEnum.UNKNOWN
        else:
            result_label = ResultLabelEnum.SAFE
        
        return {
            "result_label": result_label,
            "confidence_score": min(risk_score + 20, 95),  # Confidence based on risk
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "reason": ", ".join(risk_factors) if risk_factors else "No specific risk factors identified",
            "detection_method": "heuristic_analysis",
            "processing_time": 0.1  # Placeholder
        }
    
    def _create_detection_result(self, scan_request_id: int, source_type: SourceTypeEnum,
                                source_id: int, ai_analysis: Dict[str, Any]) -> ScamDetectionResult:
        """
        Create a detection result record
        """
        detection_result = ScamDetectionResult(
            scan_request_id=scan_request_id,
            source_type=source_type,
            source_id=source_id,
            result_label=ai_analysis["result_label"],
            confidence_score=ai_analysis["confidence_score"],
            detection_method=ai_analysis["detection_method"],
            analysis_details=ai_analysis["reason"],
            risk_score=ai_analysis["risk_score"],
            ai_model_version="v1.0",
            processing_time=ai_analysis["processing_time"]
        )
        
        self.db.add(detection_result)
        self.db.commit()
        self.db.refresh(detection_result)
        
        return detection_result
    
    def _get_recommendation(self, ai_analysis: Dict[str, Any], phone_check: Dict[str, Any]) -> str:
        """
        Generate recommendation based on analysis results
        """
        if ai_analysis["result_label"] == ResultLabelEnum.SCAM:
            return "BLOCK: This number has been identified as a scam. Do not answer or call back."
        elif ai_analysis["result_label"] == ResultLabelEnum.SUSPICIOUS:
            return "CAUTION: This number shows suspicious patterns. Proceed with caution."
        elif phone_check["is_flagged"]:
            return "WARNING: This number has been flagged in our database. Avoid contact."
        else:
            return "SAFE: No immediate concerns detected, but remain vigilant."
    
    def get_detection_history(self, user_id: int, limit: int = 50) -> Dict[str, Any]:
        """
        Get user's scam detection history
        """
        try:
            # Get recent scan requests
            scan_requests = self.db.query(ScanRequest).filter(
                ScanRequest.user_id == user_id
            ).order_by(ScanRequest.timestamp.desc()).limit(limit).all()
            
            # Get detection results
            detection_results = self.db.query(ScamDetectionResult).filter(
                ScamDetectionResult.scan_request_id.in_([sr.id for sr in scan_requests])
            ).all()
            
            # Get alerts
            alerts = self.alert_service.get_user_alerts(user_id, limit=limit)
            
            return {
                "scan_requests": len(scan_requests),
                "detection_results": len(detection_results),
                "alerts": len(alerts),
                "recent_scans": [
                    {
                        "id": sr.id,
                        "source_from": sr.source_from,
                        "source_type": sr.source_type,
                        "status": sr.status,
                        "timestamp": sr.timestamp.isoformat()
                    } for sr in scan_requests
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting detection history: {str(e)}")
            raise 