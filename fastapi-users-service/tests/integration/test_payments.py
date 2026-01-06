"""
Integration tests for payments routes.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestPaymentsEndpoint:
    """Test cases for payments endpoint."""

    def test_make_payment_success(self, client: TestClient):
        """Test successful payment (mocked random to always succeed)."""
        payment_data = {
            "user_id": 1,
            "amount": 100.0,
        }
        
        # Mock random to return 2 (success path)
        with patch("app.routes.payments.random.randint", return_value=2):
            response = client.post("/api/v1/payments/", json=payment_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == 1
        assert data["amount"] == 100.0
        assert data["status"] == "success"

    def test_make_payment_failure(self, client: TestClient):
        """Test payment failure (mocked random to always fail)."""
        payment_data = {
            "user_id": 1,
            "amount": 100.0,
        }
        
        # Mock random to return 1 (failure path)
        with patch("app.routes.payments.random.randint", return_value=1):
            response = client.post("/api/v1/payments/", json=payment_data)
        
        # The route raises PaymentException which returns 402
        assert response.status_code == 402

    def test_make_payment_invalid_data(self, client: TestClient):
        """Test payment with invalid data fails."""
        payment_data = {
            "user_id": "invalid",  # Should be int
            "amount": 100.0,
        }
        
        response = client.post("/api/v1/payments/", json=payment_data)
        
        assert response.status_code == 422

