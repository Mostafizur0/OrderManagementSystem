from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from typing import List, Optional


class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user: UserCreate, password_hash: str) -> User:
        """Create a new user with hashed password."""
        db_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password_hash=password_hash
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(
        db: Session, user_id: int, user: UserUpdate
    ) -> Optional[User]:
        """Update a user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user.model_dump(exclude_unset=True, exclude={"password"})
            
            # Handle password update separately
            if user.password:
                update_data["password_hash"] = hash_password(user.password)
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
