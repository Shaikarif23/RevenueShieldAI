from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.tracking import Tracking
from app.models.order import Order
from app.models.user import User

from app.schemas.tracking import (
    TrackingCreate,
    TrackingUpdate,
    TrackingResponse
)

from app.utils.roles import require_role


router = APIRouter(
    prefix="/tracking",
    tags=["Tracking"]
)


# ======================================
# CREATE TRACKING
# DELIVERY PARTNER ONLY
# ======================================

@router.post(
    "/",
    response_model=TrackingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tracking(
    tracking: TrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DELIVERY_PARTNER"))
):

    order = (
        db.query(Order)
        .filter(Order.id == tracking.order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    new_tracking = Tracking(
        order_id=tracking.order_id,
        status=tracking.status,
        latitude=tracking.latitude,
        longitude=tracking.longitude
    )

    db.add(new_tracking)
    db.commit()
    db.refresh(new_tracking)

    return new_tracking


# ======================================
# GET ALL TRACKING RECORDS
# ======================================

@router.get(
    "/",
    response_model=List[TrackingResponse]
)
def get_all_tracking(
    db: Session = Depends(get_db)
):

    return db.query(Tracking).all()


# ======================================
# GET TRACKING BY ID
# ======================================

@router.get(
    "/{tracking_id}",
    response_model=TrackingResponse
)
def get_tracking(
    tracking_id: int,
    db: Session = Depends(get_db)
):

    tracking = (
        db.query(Tracking)
        .filter(Tracking.id == tracking_id)
        .first()
    )

    if tracking is None:
        raise HTTPException(
            status_code=404,
            detail="Tracking record not found"
        )

    return tracking


# ======================================
# GET TRACKING HISTORY OF AN ORDER
# ======================================

@router.get(
    "/order/{order_id}",
    response_model=List[TrackingResponse]
)
def get_order_tracking(
    order_id: int,
    db: Session = Depends(get_db)
):

    return (
        db.query(Tracking)
        .filter(Tracking.order_id == order_id)
        .all()
    )


# ======================================
# UPDATE TRACKING
# DELIVERY PARTNER ONLY
# ======================================

@router.put(
    "/{tracking_id}",
    response_model=TrackingResponse
)
def update_tracking(
    tracking_id: int,
    tracking_data: TrackingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DELIVERY_PARTNER"))
):

    tracking = (
        db.query(Tracking)
        .filter(Tracking.id == tracking_id)
        .first()
    )

    if tracking is None:
        raise HTTPException(
            status_code=404,
            detail="Tracking record not found"
        )

    tracking.status = tracking_data.status
    tracking.latitude = tracking_data.latitude
    tracking.longitude = tracking_data.longitude

    db.commit()
    db.refresh(tracking)

    return tracking


# ======================================
# DELETE TRACKING
# DELIVERY PARTNER ONLY
# ======================================

@router.delete("/{tracking_id}")
def delete_tracking(
    tracking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DELIVERY_PARTNER"))
):

    tracking = (
        db.query(Tracking)
        .filter(Tracking.id == tracking_id)
        .first()
    )

    if tracking is None:
        raise HTTPException(
            status_code=404,
            detail="Tracking record not found"
        )

    db.delete(tracking)
    db.commit()

    return {
        "message": "Tracking record deleted successfully"
    }