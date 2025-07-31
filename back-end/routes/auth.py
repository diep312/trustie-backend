from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import request_otp, verify_otp
from passlib.hash import bcrypt


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/request-otp")
def request_otp_route(phone_number: str, db: Session = Depends(get_db)):
    if request_otp(db, phone_number):
        return {"message": "OTP sent"}
    raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-otp")
def verify_otp_route(phone_number: str, otp: str, db: Session = Depends(get_db)):
    if verify_otp(db, phone_number, otp):
        return {"message": "OTP verified"}
    raise HTTPException(status_code=400, detail="Invalid OTP")


@router.post("/set-pin")
def set_pin(phone: str, pin: str, db: Session = Depends(get_db)):
    user = db.get_user_by_phone(phone)
    if user.pin_hash:
        raise HTTPException(400, "PIN already set")
    
    hashed_pin = hash_pin(pin)
    db.update_pin(user.id, hashed_pin)
    return {"message": "PIN set successfully"}


@router.post("/login")
def login_with_pin(phone: str, pin: str, device_id: str, db: Session = Depends(get_db)):
    user = db.get_user_by_phone(phone)
    if not user or not verify_pin(pin, user.pin_hash):
        raise HTTPException(401, "Invalid login")

    if user.current_device_id != device_id:
        return {"message": "New device detected. OTP required"}

    return {"message": "Login successful"}
