"""
Integration tests for authentication routes.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAuthRegister:
    """Test cases for user registration endpoint."""

    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "phone": "+1234567890",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with existing email fails."""
        user_data = {
            "name": "Another User",
            "email": test_user.email,
            "password": "password123",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 409

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email fails."""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test registration with too short password fails."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "123",  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422


@pytest.mark.integration
class TestAuthLogin:
    """Test cases for user login endpoint."""

    def test_login_success(
        self, client: TestClient, test_user, test_user_data: dict
    ):
        """Test successful login."""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(
        self, client: TestClient, test_user, test_user_data: dict
    ):
        """Test login with wrong password fails."""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent email fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401


@pytest.mark.integration
class TestAuthRefresh:
    """Test cases for token refresh endpoint."""

    def test_refresh_token_success(
        self, client: TestClient, test_user, test_user_data: dict
    ):
        """Test successful token refresh."""
        # First, login to get tokens
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Refresh the token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token fails."""
        refresh_data = {"refresh_token": "invalid-refresh-token"}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401


@pytest.mark.integration
class TestAuthLogout:
    """Test cases for logout endpoint."""

    def test_logout_success(
        self, client: TestClient, test_user, test_user_data: dict
    ):
        """Test successful logout."""
        # First, login to get tokens
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Logout
        logout_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/api/v1/auth/logout", json=logout_data)
        
        assert response.status_code == 204


@pytest.mark.integration
class TestAuthMe:
    """Test cases for /me endpoint."""

    def test_get_current_user(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test getting current authenticated user."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_current_user_no_token(self, client: TestClient):
        """Test /me endpoint without token fails."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test /me endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401

