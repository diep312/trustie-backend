#!/usr/bin/env python3
"""
Test script for the report functionality
This script demonstrates how to use the report endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_phone_report():
    """Test reporting a phone number"""
    print("Testing phone report...")
    
    url = f"{BASE_URL}/reports/phone"
    data = {
        "phone_number": "+1234567890",
        "reason": "Suspicious calls asking for personal information",
        "user_id": 1,
        "priority": "high"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_website_report():
    """Test reporting a website"""
    print("\nTesting website report...")
    
    url = f"{BASE_URL}/reports/website"
    data = {
        "domain": "suspicious-site.com",
        "reason": "Phishing website asking for login credentials",
        "user_id": 1,
        "priority": "high",
        "url": "https://suspicious-site.com/login"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_sms_report():
    """Test reporting an SMS"""
    print("\nTesting SMS report...")
    
    url = f"{BASE_URL}/reports/sms"
    data = {
        "sender_phone": "+1987654321",
        "reason": "Suspicious SMS claiming prize win",
        "user_id": 1,
        "priority": "medium",
        "message_body": "You have won $1000! Click here to claim: http://fake-link.com"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_user_reports():
    """Test getting reports for a user"""
    print("\nTesting get user reports...")
    
    url = f"{BASE_URL}/reports/user/1"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_reports_by_type():
    """Test getting reports by type"""
    print("\nTesting get reports by type (phone)...")
    
    url = f"{BASE_URL}/reports/type/phone"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Run all tests"""
    print("=== Report Functionality Test ===\n")
    
    # Test creating reports
    phone_report = test_phone_report()
    website_report = test_website_report()
    sms_report = test_sms_report()
    
    # Test retrieving reports
    user_reports = test_get_user_reports()
    phone_reports = test_get_reports_by_type()
    
    print("\n=== Test Summary ===")
    print(f"Phone report created: {'Yes' if phone_report else 'No'}")
    print(f"Website report created: {'Yes' if website_report else 'No'}")
    print(f"SMS report created: {'Yes' if sms_report else 'No'}")
    print(f"User reports retrieved: {'Yes' if user_reports else 'No'}")
    print(f"Phone reports retrieved: {'Yes' if phone_reports else 'No'}")

if __name__ == "__main__":
    main() 