from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.customer import Customer
from app.models.order import Order
from app.models.user import User

from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse
)
from app.schemas.order import OrderResponse

from app.utils.roles import require_role


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


# ======================================
# CREATE CUSTOMER PROFILE
# CUSTOMER ONLY
# ======================================

@router.post(
    "/profile",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer_profile(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):

    # Prevent duplicate profile
    existing_customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer profile already exists"
        )

    new_customer = Customer(
        user_id=current_user.id,
        default_address=customer.default_address,
        city=customer.city,
        latitude=customer.latitude,
        longitude=customer.longitude
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


# ======================================
# CUSTOMER ORDER HISTORY
# CUSTOMER CAN ACCESS ONLY OWN ORDERS
# ======================================

@router.get(
    "/{customer_id}/orders",
    response_model=List[OrderResponse]
)
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Ownership validation
    if customer.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another customer's orders"
        )

    orders = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .all()
    )

    return orders