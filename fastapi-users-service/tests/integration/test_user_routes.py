"""
Integration tests for user management routes.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestCreateUser:
    """Test cases for user creation endpoint."""

    def test_create_user_success(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test successful user creation."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "phone": "+1234567890",
            "password": "securepassword123",
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_create_user_duplicate_email(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test creating user with existing email fails."""
        user_data = {
            "name": "Another User",
            "email": test_user.email,
            "password": "password123",
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 409

    def test_create_user_unauthorized(self, client: TestClient):
        """Test creating user without authentication fails."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 403


@pytest.mark.integration
class TestGetUsers:
    """Test cases for getting users endpoint."""

    def test_get_users_empty(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test getting users when only test user exists."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1  # Only test_user exists

    def test_get_users_with_pagination(
        self, client: TestClient, multiple_users, auth_headers: dict
    ):
        """Test getting users with pagination."""
        response = client.get(
            "/api/v1/users/?skip=1&limit=2",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_users_unauthorized(self, client: TestClient):
        """Test getting users without authentication fails."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 403


@pytest.mark.integration
class TestGetUser:
    """Test cases for getting a single user endpoint."""

    def test_get_user_success(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test getting a specific user."""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_user_not_found(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test getting a non-existent user fails."""
        response = client.get(
            "/api/v1/users/99999",
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    def test_get_user_unauthorized(
        self, client: TestClient, test_user
    ):
        """Test getting user without authentication fails."""
        response = client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 403


@pytest.mark.integration
class TestUpdateUser:
    """Test cases for updating user endpoint."""

    def test_update_user_name(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test updating user name."""
        update_data = {"name": "Updated Name"}
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_user_email(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test updating user email."""
        update_data = {"email": "updated@example.com"}
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"

    def test_update_user_not_found(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test updating a non-existent user fails."""
        update_data = {"name": "Updated Name"}
        
        response = client.put(
            "/api/v1/users/99999",
            json=update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    def test_update_user_unauthorized(
        self, client: TestClient, test_user
    ):
        """Test updating user without authentication fails."""
        update_data = {"name": "Updated Name"}
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
        )
        
        assert response.status_code == 403


@pytest.mark.integration
class TestDeleteUser:
    """Test cases for deleting user endpoint."""

    def test_delete_user_success(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test deleting a user."""
        response = client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_user_not_found(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        """Test deleting a non-existent user fails."""
        response = client.delete(
            "/api/v1/users/99999",
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    def test_delete_user_unauthorized(
        self, client: TestClient, test_user
    ):
        """Test deleting user without authentication fails."""
        response = client.delete(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 403

