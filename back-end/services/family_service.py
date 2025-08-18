from sqlalchemy.orm import Session
from ..models.user import User 
from ..models.family import FamilyMember
from fastapi import HTTPException
from datetime import datetime
import re



def link_family_member(
    scanned_payload: str,
    family_user_id: int,
    db: Session
):
    """
    Link a family member to an elderly user based on QR code scan.
    The scanned payload contains the elder's ID, and elder's information is fetched from User table.
    """
    try:
        elderly_user_id = int(scanned_payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid QR payload")

    # Fetch elder user information from User table
    elderly_user = db.query(User).filter(User.id == elderly_user_id, User.is_elderly == True).first()
    if not elderly_user:
        raise HTTPException(status_code=404, detail="Elderly user not found")

    # Fetch family user information
    family_user = db.query(User).filter(User.id == family_user_id).first()
    if not family_user:
        raise HTTPException(status_code=404, detail="Family user not found")

    # Check if already linked
    existing_link = db.query(FamilyMember).filter(
        FamilyMember.user_id == elderly_user_id,
        FamilyMember.linked_user_id == family_user_id
    ).first()
    if existing_link:
        raise HTTPException(status_code=409, detail="Người dùng đã kết nối")

    # Create family link using elder's information from User table
    family_link = FamilyMember(
        name=elderly_user.name,  # Use elder's name from User table
        relation_type="family_member",  # Default relationship type
        phone_number=None,  # Phone number will be set separately if needed
        email=elderly_user.email,  # Use elder's email from User table
        notify_on_alert=True,
        is_primary_contact=True,
        user_id=elderly_user_id,
        linked_user_id=family_user_id
    )
    db.add(family_link)
    db.commit()
    db.refresh(family_link)

    return {
        "message": "Kết nối với thành viên gia đình thành công!",
        "elderly_user": {
            "id": elderly_user.id,
            "name": elderly_user.name,
            "email": elderly_user.email
        },
        "family_user": {
            "id": family_user.id,
            "name": family_user.name
        }
    }

def check_if_linked(elderly_user_id: int, family_user_id: int, db: Session):
    link = db.query(FamilyMember).filter(
        FamilyMember.user_id == elderly_user_id,
        FamilyMember.linked_user_id == family_user_id
    ).first()

    return {
        "linked": bool(link),
        "link_id": link.id if link else None,
        "notify_on_alert": link.notify_on_alert if link else None
    }

def unlink_family(elderly_user_id: int, family_user_id: int, db: Session):
    link = db.query(FamilyMember).filter(
        FamilyMember.user_id == elderly_user_id,
        FamilyMember.linked_user_id == family_user_id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="No existing link found")

    db.delete(link)
    db.commit()
    return {"message": "Family member unlinked successfully"}

def get_elderly_user_info(elderly_user_id: int, db: Session):
    """
    Get elderly user information for display purposes.
    This can be used to show elder's details before linking.
    """
    elderly_user = db.query(User).filter(User.id == elderly_user_id, User.is_elderly == True).first()
    if not elderly_user:
        raise HTTPException(status_code=404, detail="Elderly user not found")
    
    return {
        "id": elderly_user.id,
        "name": elderly_user.name,
        "email": elderly_user.email,
        "is_elderly": elderly_user.is_elderly,
        "is_active": elderly_user.is_active
    }

def get_linked_family_members(elderly_user_id: int, db: Session):
    elderly_user = db.query(User).filter(User.id == elderly_user_id, User.is_elderly == True).first()
    if not elderly_user:
        raise HTTPException(status_code=404, detail="Elderly user not found")

    members = (
        db.query(FamilyMember)
        .filter(FamilyMember.user_id == elderly_user_id)
        .all()
    )

    # Build the response list
    family_list = []
    for member in members:
        # Get the family member's user information
        family_user = db.query(User).filter(User.id == member.linked_user_id).first()
        if family_user:
            family_list.append({
                "user_id": member.linked_user_id,     # The linked user's account id
                "name": family_user.name,             # Family member's name from User table
                "phoneNumber": member.phone_number,
                "relationship": member.relation_type  # Your model column is relation_type
            })

    return family_list


def get_linked_family_members_for_alert(elderly_user_id: int, db: Session):
    """
    Returns all linked family members for an elderly.
    """
    return db.query(FamilyMember).filter(
        FamilyMember.user_id == elderly_user_id
    ).all()
