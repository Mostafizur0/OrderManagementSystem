"""
Pytest configuration and shared fixtures for testing.

This module creates test-specific models without PostgreSQL schema constraints
and patches the app to use them during testing, keeping production code unchanged.
"""
import os

# Set test environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")

import pytest
from typing import Generator, Any
from unittest.mock import MagicMock
from datetime import datetime, timezone

from sqlalchemy import create_engine, StaticPool, DateTime, func, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship
from fastapi.testclient import TestClient


# Create test-specific Base without schema (SQLite compatible)
class TestBase(DeclarativeBase):
    pass


# Test-specific User model (mirrors app.models.users.User but without schema)
class TestUser(TestBase):
    __tablename__ = "user"
    __table_args__ = {}  # No schema for SQLite compatibility
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    
    refreshtoken: Mapped[list["TestRefreshToken"]] = relationship(
        "TestRefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# Test-specific RefreshToken model (mirrors app.models.refresh_token.RefreshToken but without schema)
class TestRefreshToken(TestBase):
    __tablename__ = "refreshtoken"
    __table_args__ = {}  # No schema for SQLite compatibility
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    user: Mapped["TestUser"] = relationship("TestUser", back_populates="refreshtoken")


# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def patch_app_models():
    """
    Patch app modules to use test models instead of production models.
    This allows tests to work with SQLite while keeping production code unchanged.
    Returns dict of original models for restoration.
    """
    import app.models.users
    import app.models.refresh_token
    import app.crud.user
    import app.crud.auth
    import app.routes.auth
    import app.routes.users
    import app.core.security
    
    # Store originals for restoration
    originals = {
        'app.models.users.User': app.models.users.User,
        'app.models.refresh_token.RefreshToken': app.models.refresh_token.RefreshToken,
        'app.routes.auth.UserModel': getattr(app.routes.auth, 'UserModel', None),
        'app.core.security.User': getattr(app.core.security, 'User', None),
    }
    
    # Patch models in their modules
    app.models.users.User = TestUser
    app.models.refresh_token.RefreshToken = TestRefreshToken
    
    # Patch UserModel alias in routes.auth (which is imported by routes.users)
    app.routes.auth.UserModel = TestUser
    
    # Patch security module
    app.core.security.User = TestUser
    
    return originals


def unpatch_app_models(originals):
    """Restore original models."""
    import app.models.users
    import app.models.refresh_token
    import app.routes.auth
    import app.core.security
    
    app.models.users.User = originals['app.models.users.User']
    app.models.refresh_token.RefreshToken = originals['app.models.refresh_token.RefreshToken']
    
    if originals['app.routes.auth.UserModel'] is not None:
        app.routes.auth.UserModel = originals['app.routes.auth.UserModel']
    
    if originals['app.core.security.User'] is not None:
        app.core.security.User = originals['app.core.security.User']


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Tables are created before each test and dropped after.
    """
    # Create all tables using test models
    TestBase.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        TestBase.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with overridden database dependency and patched models.
    """
    from main import app
    from app.database import get_db
    
    # Patch models for this test
    originals = patch_app_models()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original models
    unpatch_app_models(originals)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "password": "testpassword123",
    }


@pytest.fixture
def test_user(db_session: Session, test_user_data: dict) -> TestUser:
    """Create a test user in the database."""
    from app.core.security import hash_password
    
    user = TestUser(
        name=test_user_data["name"],
        email=test_user_data["email"],
        phone=test_user_data["phone"],
        password_hash=hash_password(test_user_data["password"]),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: TestUser) -> str:
    """Generate an authentication token for the test user."""
    from app.core.security import create_access_token
    
    token_data = {"sub": str(test_user.id), "email": test_user.email}
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Return authorization headers with bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def authenticated_client(
    client: TestClient,
    auth_headers: dict[str, str],
) -> TestClient:
    """
    Return a test client with authentication headers set.
    """
    original_request = client.request
    
    def request_with_auth(*args, **kwargs):
        headers = kwargs.get("headers", {})
        headers.update(auth_headers)
        kwargs["headers"] = headers
        return original_request(*args, **kwargs)
    
    client.request = request_with_auth
    return client


@pytest.fixture
def multiple_users(db_session: Session) -> list[TestUser]:
    """Create multiple test users in the database."""
    from app.core.security import hash_password
    
    users = []
    for i in range(5):
        user = TestUser(
            name=f"User {i}",
            email=f"user{i}@example.com",
            phone=f"+123456789{i}",
            password_hash=hash_password(f"password{i}"),
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    
    return users


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Create a mock database session for unit tests."""
    return MagicMock(spec=Session)


# Marker helpers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
