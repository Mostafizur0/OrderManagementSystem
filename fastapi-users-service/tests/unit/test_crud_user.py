"""
Unit tests for UserCRUD operations.
"""
import pytest
from sqlalchemy.orm import Session

from app.crud.user import UserCRUD
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


@pytest.mark.unit
class TestUserCRUD:
    """Test cases for UserCRUD class."""

    def test_create_user_success(self, db_session: Session):
        """Test creating a new user."""
        user_data = UserCreate(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            password="securepassword123",
        )
        password_hash = hash_password(user_data.password)
        
        user = UserCRUD.create_user(db_session, user_data, password_hash)
        
        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.phone == "+1234567890"
        assert user.password_hash == password_hash

    def test_get_user_by_id(self, db_session: Session, test_user):
        """Test retrieving a user by ID."""
        user = UserCRUD.get_user(db_session, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_not_found(self, db_session: Session):
        """Test getting a non-existent user returns None."""
        user = UserCRUD.get_user(db_session, 99999)
        
        assert user is None

    def test_get_user_by_email(self, db_session: Session, test_user):
        """Test retrieving a user by email."""
        user = UserCRUD.get_user_by_email(db_session, test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_email_not_found(self, db_session: Session):
        """Test getting a user by non-existent email returns None."""
        user = UserCRUD.get_user_by_email(db_session, "nonexistent@example.com")
        
        assert user is None

    def test_get_users_empty(self, db_session: Session):
        """Test getting users when database is empty."""
        users = UserCRUD.get_users(db_session)
        
        assert users == []

    def test_get_users_with_data(self, db_session: Session, multiple_users):
        """Test getting all users."""
        users = UserCRUD.get_users(db_session)
        
        assert len(users) == 5

    def test_get_users_pagination(self, db_session: Session, multiple_users):
        """Test pagination in get_users."""
        users = UserCRUD.get_users(db_session, skip=2, limit=2)
        
        assert len(users) == 2

    def test_update_user_name(self, db_session: Session, test_user):
        """Test updating user name."""
        update_data = UserUpdate(name="Updated Name")
        
        updated_user = UserCRUD.update_user(db_session, test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        assert updated_user.email == test_user.email  # Unchanged

    def test_update_user_email(self, db_session: Session, test_user):
        """Test updating user email."""
        update_data = UserUpdate(email="newemail@example.com")
        
        updated_user = UserCRUD.update_user(db_session, test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.email == "newemail@example.com"

    def test_update_user_not_found(self, db_session: Session):
        """Test updating a non-existent user returns None."""
        update_data = UserUpdate(name="New Name")
        
        result = UserCRUD.update_user(db_session, 99999, update_data)
        
        assert result is None

    def test_delete_user_success(self, db_session: Session, test_user):
        """Test deleting a user."""
        result = UserCRUD.delete_user(db_session, test_user.id)
        
        assert result is True
        assert UserCRUD.get_user(db_session, test_user.id) is None

    def test_delete_user_not_found(self, db_session: Session):
        """Test deleting a non-existent user returns False."""
        result = UserCRUD.delete_user(db_session, 99999)
        
        assert result is False

    def test_create_multiple_users(self, db_session: Session):
        """Test creating multiple users."""
        for i in range(3):
            user_data = UserCreate(
                name=f"User {i}",
                email=f"user{i}@test.com",
                password="password123",
            )
            password_hash = hash_password(user_data.password)
            UserCRUD.create_user(db_session, user_data, password_hash)
        
        users = UserCRUD.get_users(db_session)
        
        assert len(users) == 3

