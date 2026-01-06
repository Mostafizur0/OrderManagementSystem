"""
Integration tests for health and root endpoints.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "FastAPI Users Service"
        assert "version" in data


@pytest.mark.integration
class TestRootEndpoint:
    """Test cases for root endpoint."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "health" in data

