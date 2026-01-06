from app.schemas.order import OrderCreate, OrderRead, OrderPayload
from app.dependencies.auth import get_current_user
from app.crud.orders import (
    create_order as crud_create_order, 
    get_order, 
    get_orders_by_user,
    update_order as crud_update_order,
    delete_order as crud_delete_order
)
from app.services.user_service import verify_user_exists
from app.database import get_db
from app.middleware.metrics_middleware import ORDERS_CREATED_TOTAL
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel


order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post("/", response_model=OrderRead)
async def create_order(
    order: OrderPayload, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order with user verification and database persistence
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")  # Get the raw token from current_user
    
    # Verify user exists in users-service
    user_exists = await verify_user_exists(user_id, token)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in users service"
        )
    
    # Create order data
    order_data = OrderCreate(
        customer_id=user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        price=order.price
    )
    
    # Save to database
    db_order = crud_create_order(db=db, order=order_data)
    
    # Increment orders created metric
    ORDERS_CREATED_TOTAL.inc()
    
    return db_order


@order_router.get("/", response_model=list[OrderRead])
async def get_user_orders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for the current authenticated user
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    
    # Verify user exists in users-service
    user_exists = await verify_user_exists(user_id, token)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in users service"
        )
    
    # Get user's orders
    orders = get_orders_by_user(db=db, user_id=user_id)
    return orders


@order_router.get("/{order_id}", response_model=OrderRead)
async def get_order_details(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific order (only if it belongs to the current user)
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    
    # Verify user exists in users-service
    user_exists = await verify_user_exists(user_id, token)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in users service"
        )
    
    # Get order
    order = get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to current user
    if order.customer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: This order does not belong to you"
        )
    
    return order


@order_router.put("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: int,
    order_update: OrderPayload,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing order (only if it belongs to the current user)
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    
    # Verify user exists in users-service
    user_exists = await verify_user_exists(user_id, token)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in users service"
        )
    
    # Create order update data
    order_data = OrderCreate(
        customer_id=user_id,
        product_id=order_update.product_id,
        quantity=order_update.quantity,
        price=order_update.price
    )
    
    # Update order
    updated_order = crud_update_order(db=db, order_id=order_id, user_id=user_id, order_update=order_data)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or access denied"
        )
    
    return updated_order


@order_router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an order (only if it belongs to the current user)
    """
    user_id = current_user["user_id"]
    token = current_user.get("token")
    
    # Verify user exists in users-service
    user_exists = await verify_user_exists(user_id, token)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in users service"
        )
    
    # Delete order
    deleted = crud_delete_order(db=db, order_id=order_id, user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or access denied"
        )
    
    return {"message": "Order deleted successfully"}
