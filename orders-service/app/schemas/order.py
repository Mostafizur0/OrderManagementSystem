from pydantic import BaseModel, EmailStr
from typing import Optional


class OrderBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderPayload(OrderBase):
    pass

class OrderCreate(OrderBase):
    customer_id: int


class OrderRead(OrderBase):
    id: int
    customer_id: int
