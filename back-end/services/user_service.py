from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..schemas import UserCreate, User as UserSchema
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        try:
            user = User(
                name=user_data.name,
                email=user_data.email,
                device_id=user_data.device_id,
                is_elderly=user_data.is_elderly,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_data: UserCreate) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        try:
            user.name = user_data.name
            user.email = user_data.email
            user.device_id = user_data.device_id
            user.is_elderly = user_data.is_elderly
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            raise

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise