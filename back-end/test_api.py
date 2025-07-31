#!/usr/bin/env python3
"""
Test script for Trustie Backend API
This script demonstrates the phone number checking and alert functionality
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_phone_check():
    """Test phone number checking functionality"""
    print("=== Testing Phone Number Check ===")
    
    # Test data
    test_phones = [
        "+18005551234",  # US toll-free (suspicious)
        "+12345678901",  # Regular US number
        "+447911123456",  # UK number (international)
        "555-1234",      # Local number
    ]
    
    for phone in test_phones:
        print(f"\nChecking phone: {phone}")
        
        # Test basic phone check
        response = requests.post(f"{BASE_URL}/phone/check", json={
            "phone_number": phone,
            "user_id": 1
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Found: {result['found']}")
            print(f"  Flagged: {result['is_flagged']}")
            print(f"  Risk Score: {result['risk_score']}")
            if result.get('flag_reason'):
                print(f"  Reason: {result['flag_reason']}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")

def test_scam_detection():
    """Test comprehensive scam detection"""
    print("\n=== Testing Scam Detection ===")
    
    # Test scam detection with context
    test_cases = [
        {
            "phone_number": "+18005551234",
            "context": "Caller says my social security account is suspended"
        },
        {
            "phone_number": "+12345678901",
            "context": "Regular call from friend"
        }
    ]
    
    for case in test_cases:
        print(f"\nDetecting scam for: {case['phone_number']}")
        print(f"Context: {case['context']}")
        
        response = requests.post(f"{BASE_URL}/scam-detection/detect", json={
            "phone_number": case["phone_number"],
            "user_id": 1,
            "context": case["context"]
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"  AI Analysis: {result['ai_analysis']['result_label']}")
            print(f"  Risk Score: {result['ai_analysis']['risk_score']}")
            print(f"  Alert Created: {result['alert_created']}")
            print(f"  Recommendation: {result['recommendation']}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")

def test_alerts():
    """Test alert functionality"""
    print("\n=== Testing Alerts ===")
    
    # Get user alerts
    response = requests.get(f"{BASE_URL}/alerts/user/1")
    
    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts for user")
        
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"  Alert {alert['id']}: {alert['message']}")
            print(f"    Type: {alert['alert_type']}, Severity: {alert['severity']}")
            print(f"    Read: {alert['is_read']}, Acknowledged: {alert['is_acknowledged']}")
    else:
        print(f"Error getting alerts: {response.status_code} - {response.text}")

def test_risk_assessment():
    """Test risk assessment without creating alerts"""
    print("\n=== Testing Risk Assessment ===")
    
    test_phone = "+18005551234"
    
    response = requests.get(f"{BASE_URL}/scam-detection/risk-assessment/{test_phone}?context=urgent call about account")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Phone: {result['phone_number']}")
        print(f"Overall Risk Score: {result['overall_risk_score']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"AI Confidence: {result['ai_analysis']['confidence_score']}%")
    else:
        print(f"Error in risk assessment: {response.status_code} - {response.text}")

def test_stats():
    """Test detection statistics"""
    print("\n=== Testing Detection Stats ===")
    
    response = requests.get(f"{BASE_URL}/scam-detection/stats/1")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Scans: {stats['total_scans']}")
        print(f"Total Alerts: {stats['total_alerts']}")
        print(f"Success Rate: {stats['success_rate']}%")
        print(f"Recent Activity: {stats['recent_activity']} scans")
    else:
        print(f"Error getting stats: {response.status_code} - {response.text}")

def main():
    """Run all tests"""
    print("Trustie Backend API Test Suite")
    print("=" * 40)
    
    try:
        # Test basic functionality
        test_phone_check()
        test_scam_detection()
        test_risk_assessment()
        test_alerts()
        test_stats()
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: uvicorn main:app --reload")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main() 