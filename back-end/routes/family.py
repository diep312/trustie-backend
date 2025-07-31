from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.family_service import link_family_member, check_if_linked, unlink_family
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/family", tags=["family"])



class LinkRequest(BaseModel):
    scanned_payload: str
    family_user_id: int
    name: str
    relationship: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


@router.post("/link-family")
def link_family(data: LinkRequest, db: Session = Depends(get_db)):
    return link_family_member(
        scanned_payload=data.scanned_payload,
        family_user_id=data.family_user_id,
        name=data.name,
        relationship=data.relationship,
        phone_number=data.phone_number,
        email=data.email,
        db=db
    )


@router.get("/link-status/{elderly_user_id}/{family_user_id}")
def check_link_status(elderly_user_id: int, family_user_id: int, db: Session = Depends(get_db)):
    return check_if_linked(elderly_user_id, family_user_id, db)


@router.delete("/unlink-family/{elderly_user_id}/{family_user_id}")
def unlink_family_member(elderly_user_id: int, family_user_id: int, db: Session = Depends(get_db)):
    return unlink_family(elderly_user_id, family_user_id, db)
