from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.models.user import User

from app.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerResponse,
)

from app.schemas.order import OrderResponse

from app.utils.roles import require_role


router = APIRouter(
    prefix="/delivery-partners",
    tags=["Delivery Partners"],
)


# ======================================
# CREATE DELIVERY PARTNER
# DELIVERY_PARTNER ONLY
# ======================================

@router.post(
    "/",
    response_model=DeliveryPartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_delivery_partner(
    partner: DeliveryPartnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("DELIVERY_PARTNER")
    )
):

    # Prevent duplicate profile
    existing_partner = (
        db.query(DeliveryPartner)
        .filter(
            DeliveryPartner.user_id == current_user.id
        )
        .first()
    )

    if existing_partner:
        raise HTTPException(
            status_code=400,
            detail="Delivery partner profile already exists"
        )

    # Prevent duplicate vehicle number
    existing_vehicle = (
        db.query(DeliveryPartner)
        .filter(
            DeliveryPartner.vehicle_number == partner.vehicle_number
        )
        .first()
    )

    if existing_vehicle:
        raise HTTPException(
            status_code=400,
            detail="Vehicle number already registered"
        )

    new_partner = DeliveryPartner(
        user_id=current_user.id,
        vehicle_type=partner.vehicle_type,
        vehicle_number=partner.vehicle_number,
        current_status="AVAILABLE",
        current_latitude=partner.current_latitude,
        current_longitude=partner.current_longitude,
    )

    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)

    return new_partner


# ======================================
# GET ALL DELIVERY PARTNERS
# PUBLIC
# ======================================

@router.get(
    "/",
    response_model=List[DeliveryPartnerResponse],
)
def get_delivery_partners(
    db: Session = Depends(get_db),
):

    return db.query(DeliveryPartner).all()


# ======================================
# GET SINGLE DELIVERY PARTNER
# PUBLIC
# ======================================

@router.get(
    "/{partner_id}",
    response_model=DeliveryPartnerResponse,
)
def get_delivery_partner(
    partner_id: int,
    db: Session = Depends(get_db),
):

    partner = (
        db.query(DeliveryPartner)
        .filter(
            DeliveryPartner.id == partner_id
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner not found",
        )

    return partner


# ======================================
# DELIVERY PARTNER ORDER HISTORY
# OWNERSHIP CHECK ENABLED
# ======================================

@router.get(
    "/{partner_id}/orders",
    response_model=List[OrderResponse]
)
def get_delivery_partner_orders(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("DELIVERY_PARTNER")
    )
):

    partner = (
        db.query(DeliveryPartner)
        .filter(
            DeliveryPartner.id == partner_id
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner not found"
        )

    # Ownership validation
    if partner.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another delivery partner's orders"
        )

    orders = (
        db.query(Order)
        .filter(
            Order.delivery_partner_id == partner_id
        )
        .all()
    )

    return orders


# ======================================
# DELETE DELIVERY PARTNER
# OWNERSHIP CHECK ENABLED
# ======================================

@router.delete("/{partner_id}")
def delete_delivery_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("DELIVERY_PARTNER")
    )
):

    partner = (
        db.query(DeliveryPartner)
        .filter(
            DeliveryPartner.id == partner_id
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner not found"
        )

    if partner.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete another delivery partner"
        )

    db.delete(partner)
    db.commit()

    return {
        "message": "Delivery partner deleted successfully"
    }