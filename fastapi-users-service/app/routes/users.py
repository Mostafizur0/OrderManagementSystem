from app.core.security import get_current_user, hash_password
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.crud.user import UserCRUD
from app.routes.auth import UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.exceptions.custom_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    DatabaseException,
)

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new user (requires authentication)
    """
    try:
        logger.info(f"Creating new user with email: {user.email}")

        # Check if user with email already exists
        existing_user = UserCRUD.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"User with email {user.email} already exists")
            raise UserAlreadyExistsException(user.email)

        # Hash password
        password_hash = hash_password(user.password)

        # Create user
        db_user = UserCRUD.create_user(db, user, password_hash)
        logger.info(f"User created successfully with ID: {db_user.id}")

        return db_user

    except UserAlreadyExistsException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise DatabaseException(f"Failed to create user: {str(e)}")


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all users with pagination
    """
    try:
        logger.info(f"Fetching users with skip={skip}, limit={limit}")
        users = UserCRUD.get_users(db, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(users)} users")
        return users

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise DatabaseException(f"Failed to fetch users: {str(e)}")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a user by ID
    """
    try:
        logger.info(f"Fetching user with ID: {user_id}")
        user = UserCRUD.get_user(db, user_id)

        if user is None:
            logger.warning(f"User with ID {user_id} not found")
            raise UserNotFoundException(user_id)

        logger.info(f"User with ID {user_id} retrieved successfully")
        return user

    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise DatabaseException(f"Failed to fetch user: {str(e)}")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a user
    """
    try:
        logger.info(f"Updating user with ID: {user_id}")

        # Check if user exists
        existing_user = UserCRUD.get_user(db, user_id)
        if existing_user is None:
            logger.warning(f"User with ID {user_id} not found for update")
            raise UserNotFoundException(user_id)

        # Check if email is being updated and if it already exists
        if user.email and user.email != existing_user.email:
            email_user = UserCRUD.get_user_by_email(db, user.email)
            if email_user:
                logger.warning(f"User with email {user.email} already exists")
                raise UserAlreadyExistsException(user.email)

        # Update user
        updated_user = UserCRUD.update_user(db, user_id, user)
        logger.info(f"User with ID {user_id} updated successfully")

        return updated_user

    except (UserNotFoundException, UserAlreadyExistsException):
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise DatabaseException(f"Failed to update user: {str(e)}")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a user
    """
    try:
        logger.info(f"Deleting user with ID: {user_id}")

        # Check if user exists
        existing_user = UserCRUD.get_user(db, user_id)
        if existing_user is None:
            logger.warning(f"User with ID {user_id} not found for deletion")
            raise UserNotFoundException(user_id)

        # Delete user
        success = UserCRUD.delete_user(db, user_id)
        if success:
            logger.info(f"User with ID {user_id} deleted successfully")
        else:
            logger.error(f"Failed to delete user with ID {user_id}")
            raise DatabaseException("Failed to delete user")

    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise DatabaseException(f"Failed to delete user: {str(e)}")
