from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.user_service import UserService
from ..schemas import UserCreate, User as UserSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        created = service.create_user(user)
        return UserSchema.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.from_orm(user)

@router.get("/", response_model=List[UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = UserService(db)
    users = service.get_users(skip=skip, limit=limit)
    return [UserSchema.from_orm(u) for u in users]

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    updated = service.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.from_orm(updated)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}