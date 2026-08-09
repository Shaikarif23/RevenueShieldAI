from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.cancellation import Cancellation
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.user import User

from app.schemas.cancellation import (
    CancellationCreate,
    CancellationUpdate,
    CancellationResponse
)

from app.utils.roles import require_role


router = APIRouter(
    prefix="/cancellations",
    tags=["Cancellations"]
)


# ======================================
# CREATE CANCELLATION
# CUSTOMER + RESTAURANT
# ======================================

@router.post(
    "/",
    response_model=CancellationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_cancellation(
    cancellation: CancellationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER", "RESTAURANT")
    )
):

    order = (
        db.query(Order)
        .filter(Order.id == cancellation.order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    existing = (
        db.query(Cancellation)
        .filter(Cancellation.order_id == cancellation.order_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Order is already cancelled"
        )

    new_cancellation = Cancellation(
        order_id=cancellation.order_id,
        cancelled_by=cancellation.cancelled_by,
        reason=cancellation.reason,
        refund_amount=cancellation.refund_amount,
        cancellation_fee=cancellation.cancellation_fee
    )

    order.status = OrderStatus.CANCELLED

    db.add(new_cancellation)
    db.commit()
    db.refresh(new_cancellation)

    return new_cancellation


# ======================================
# GET ALL CANCELLATIONS
# ======================================

@router.get(
    "/",
    response_model=List[CancellationResponse]
)
def get_cancellations(
    db: Session = Depends(get_db)
):

    return db.query(Cancellation).all()


# ======================================
# GET CANCELLATION BY ID
# ======================================

@router.get(
    "/{cancellation_id}",
    response_model=CancellationResponse
)
def get_cancellation(
    cancellation_id: int,
    db: Session = Depends(get_db)
):

    cancellation = (
        db.query(Cancellation)
        .filter(Cancellation.id == cancellation_id)
        .first()
    )

    if cancellation is None:
        raise HTTPException(
            status_code=404,
            detail="Cancellation not found"
        )

    return cancellation


# ======================================
# GET CANCELLATION BY ORDER
# ======================================

@router.get(
    "/order/{order_id}",
    response_model=CancellationResponse
)
def get_order_cancellation(
    order_id: int,
    db: Session = Depends(get_db)
):

    cancellation = (
        db.query(Cancellation)
        .filter(Cancellation.order_id == order_id)
        .first()
    )

    if cancellation is None:
        raise HTTPException(
            status_code=404,
            detail="Cancellation not found"
        )

    return cancellation


# ======================================
# UPDATE CANCELLATION
# CUSTOMER + RESTAURANT
# ======================================

@router.put(
    "/{cancellation_id}",
    response_model=CancellationResponse
)
def update_cancellation(
    cancellation_id: int,
    data: CancellationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER", "RESTAURANT")
    )
):

    cancellation = (
        db.query(Cancellation)
        .filter(Cancellation.id == cancellation_id)
        .first()
    )

    if cancellation is None:
        raise HTTPException(
            status_code=404,
            detail="Cancellation not found"
        )

    cancellation.reason = data.reason
    cancellation.refund_amount = data.refund_amount
    cancellation.cancellation_fee = data.cancellation_fee

    db.commit()
    db.refresh(cancellation)

    return cancellation


# ======================================
# DELETE CANCELLATION
# RESTAURANT ONLY
# ======================================

@router.delete("/{cancellation_id}")
def delete_cancellation(
    cancellation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RESTAURANT")
    )
):

    cancellation = (
        db.query(Cancellation)
        .filter(Cancellation.id == cancellation_id)
        .first()
    )

    if cancellation is None:
        raise HTTPException(
            status_code=404,
            detail="Cancellation not found"
        )

    db.delete(cancellation)
    db.commit()

    return {
        "message": "Cancellation deleted successfully"
    }