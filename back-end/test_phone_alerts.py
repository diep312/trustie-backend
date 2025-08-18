#!/usr/bin/env python3
"""
Test script for phone alert functionality
This script tests the new phone-based alert system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from services.phone_service import PhoneService
from services.alert_service import AlertService
from models.user import User
from models.family import FamilyMember
from models.alert import Alert
from sqlalchemy.orm import Session

def test_phone_alert_creation():
    """Test creating alerts for high-risk phone numbers"""
    print("Testing phone alert creation...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test users (elderly and family member)
        elderly_user = User(
            name="Test Elderly User",
            device_id="test_device_001",
            is_elderly=True
        )
        db.add(elderly_user)
        
        family_member_user = User(
            name="Test Family Member",
            device_id="test_device_002",
            is_elderly=False
        )
        db.add(family_member_user)
        
        db.commit()
        db.refresh(elderly_user)
        db.refresh(family_member_user)
        
        print(f"Created elderly user: {elderly_user.id}")
        print(f"Created family member user: {family_member_user.id}")
        
        # Create family relationship
        family_member = FamilyMember(
            user_id=elderly_user.id,
            linked_user_id=family_member_user.id,
            name="Test Family Member",
            relation_type="child",
            notify_on_alert=True
        )
        db.add(family_member)
        db.commit()
        db.refresh(family_member)
        
        print(f"Created family relationship: {family_member.id}")
        
        # Test phone service with high-risk number
        phone_service = PhoneService(db)
        
        # Test 1: High-risk number (80+) - should create alerts for both elderly and family
        print("\n--- Test 1: High-risk number (80+) ---")
        result1 = phone_service.check_phone_number(
            phone_number="+84901234567",  # This should trigger alerts for both
            user_id=elderly_user.id
        )
        print(f"Phone check result: {result1}")
        
        # Test 2: Medium-high risk number (60-79) - should create alerts only for family
        print("\n--- Test 2: Medium-high risk number (60-79) ---")
        result2 = phone_service.check_phone_number(
            phone_number="+84987654321",  # This should trigger family-only alerts
            user_id=elderly_user.id
        )
        print(f"Phone check result: {result2}")
        
        # Check if alerts were created
        alert_service = AlertService(db)
        
        # Get alerts for elderly user
        elderly_alerts = alert_service.get_user_alerts(elderly_user.id)
        print(f"\nElderly user alerts: {len(elderly_alerts)}")
        for alert in elderly_alerts:
            print(f"  - Alert {alert.id}: {alert.message} (Type: {alert.alert_type}, Severity: {alert.severity})")
        
        # Get alerts for family member
        family_alerts = alert_service.get_user_alerts(family_member_user.id)
        print(f"\nFamily member alerts: {len(family_alerts)}")
        for alert in family_alerts:
            print(f"  - Alert {alert.id}: {alert.message} (Type: {alert.alert_type}, Severity: {alert.severity})")
        
        print("\nPhone alert test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_phone_alert_creation()
