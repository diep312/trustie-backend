from sqlalchemy.orm import Session
from ..models.user import User 
from ..models.family import FamilyMember
from fastapi import HTTPException
from datetime import datetime
import re



def link_family_member(
    scanned_payload: str,
    family_user_id: int,
    name: str,
    relationship: str,
    phone_number: str,
    email: str,
    db: Session
):
    try:
        elderly_user_id = int(scanned_payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid QR payload")

    elderly_user = db.query(User).filter(User.id == elderly_user_id, User.is_elderly == True).first()
    family_user = db.query(User).filter(User.id == family_user_id).first()

    if not elderly_user or not family_user:
        raise HTTPException(status_code=404, detail="User(s) not found")

    # Check if already linked
    existing_link = db.query(FamilyMember).filter(
        FamilyMember.user_id == elderly_user_id,
        FamilyMember.linked_user_id == family_user_id
    ).first()
    if existing_link:
        raise HTTPException(status_code=409, message="Người dùng đã kết nốinối")

    family_link = FamilyMember(
        name=name,
        relationship=relationship,
        phone_number=phone_number,
        email=email,
        notify_on_alert=True,
        is_primary_contact=True,  # Optional business logic
        user_id=elderly_user_id,
        linked_user_id=family_user_id
    )
    db.add(family_link)
    db.commit()
    db.refresh(family_link)

    return {"message": "Kết nối với thành viên gia đình thành công!"}

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
