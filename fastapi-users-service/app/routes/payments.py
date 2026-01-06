from fastapi import APIRouter
from pydantic import BaseModel

from app.exceptions.payment_exception import PaymentException


payment_router = APIRouter(prefix="/payments", tags=["payments"])


class Payment(BaseModel):
    user_id: int
    amount: float


class PaymentResponse(BaseModel):
    user_id: int
    amount: float
    status: str = "success"


@payment_router.post("/", response_model=PaymentResponse, status_code=201)
def make_payment(payment: Payment) -> PaymentResponse:
    """
    Create a new payment
    """
    import random

    forbidden_number = random.randint(1, 2)

    if forbidden_number == 1:
        # Simulate a payment error
        raise PaymentException("Payment amount must be greater than zero")
    return PaymentResponse(**payment.model_dump(), status="success")
