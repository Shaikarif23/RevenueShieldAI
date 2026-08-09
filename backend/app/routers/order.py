from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.customer import Customer
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.payment import Payment
from app.models.restaurant import Restaurant
from app.models.user import User

from app.schemas.common import PaginatedResponse
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)

from app.utils.roles import require_role

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ======================================================
# VALID ORDER STATUS FLOW
# ======================================================

VALID_STATUS_FLOW = {
    OrderStatus.PLACED: [
        OrderStatus.ACCEPTED,
        OrderStatus.CANCELLED
    ],

    OrderStatus.ACCEPTED: [
        OrderStatus.PREPARING,
        OrderStatus.CANCELLED
    ],

    OrderStatus.PREPARING: [
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],

    OrderStatus.READY: [
        OrderStatus.PICKED_UP
    ],

    OrderStatus.PICKED_UP: [
        OrderStatus.ON_THE_WAY
    ],

    OrderStatus.ON_THE_WAY: [
        OrderStatus.DELIVERED
    ],

    OrderStatus.DELIVERED: [],

    OrderStatus.CANCELLED: []
}


# ======================================================
# CREATE ORDER
# ======================================================

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == order.restaurant_id)
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    subtotal = 0
    tax = subtotal * 0.05
    delivery_charge = 30
    total_amount = subtotal + tax + delivery_charge

    new_order = Order(
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        delivery_partner_id=None,
        subtotal=subtotal,
        tax=tax,
        delivery_charge=delivery_charge,
        total_amount=total_amount,
        status=OrderStatus.PLACED
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


# ======================================================
# GET ALL ORDERS
# ======================================================

@router.get(
    "/",
    response_model=PaginatedResponse[OrderResponse]
)
def get_orders(

    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),

    status: OrderStatus | None = None,
    customer_id: int | None = None,
    restaurant_id: int | None = None,
    delivery_partner_id: int | None = None,

    start_date: datetime | None = None,
    end_date: datetime | None = None,

    db: Session = Depends(get_db)
):

    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)

    if delivery_partner_id:
        query = query.filter(
            Order.delivery_partner_id == delivery_partner_id
        )

    if start_date:
        query = query.filter(
            Order.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Order.created_at <= end_date
        )

    total = query.count()

    skip = (page - 1) * size

    orders = (
        query
        .offset(skip)
        .limit(size)
        .all()
    )

    pages = (total + size - 1) // size

    return {
        "page": page,
        "size": size,
        "total": total,
        "pages": pages,
        "data": orders
    }


# ======================================================
# GET ORDER BY ID
# ======================================================



# ======================================================
# ASSIGN DELIVERY PARTNER
# ======================================================

# ======================================================
# ASSIGN DELIVERY PARTNER
# ======================================================

@router.put("/{order_id}/assign/{partner_id}")
def assign_delivery_partner(
    order_id: int,
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("RESTAURANT")
    )
):

    # Check if order exists
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Get logged-in restaurant
    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.user_id == current_user.id)
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant profile not found"
        )

    # Restaurant can assign only its own orders
    if order.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot assign delivery partners for another restaurant's order"
        )

    # Check if delivery partner exists
    partner = (
        db.query(DeliveryPartner)
        .filter(DeliveryPartner.id == partner_id)
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner not found"
        )

    # Prevent assigning the order twice
    if order.delivery_partner_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Delivery partner already assigned"
        )
    # Only PLACED orders can be assigned
    if order.status != OrderStatus.PLACED:
        raise HTTPException(
            status_code=400,
            detail="Only PLACED orders can be assigned to a delivery partner"
    )

    # Assign delivery partner
    order.delivery_partner_id = partner.id
    order.status = OrderStatus.ACCEPTED

    db.commit()
    db.refresh(order)

    return {
        "message": "Delivery partner assigned successfully",
        "order": order
    }

# ======================================================
# UPDATE STATUS
# ======================================================

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "RESTAURANT",
            "DELIVERY_PARTNER"
        )
    )
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    allowed = VALID_STATUS_FLOW.get(order.status, [])

    if status_data.status not in allowed:
        raise HTTPException(
           status_code=400,
           detail=f"Invalid status transition from {order.status.value} to {status_data.status.value}"
    )

    # Restaurant can update only its own orders and only through READY.
    if current_user.role == "RESTAURANT":

        restaurant = (
            db.query(Restaurant)
            .filter(Restaurant.user_id == current_user.id)
            .first()
        )

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant profile not found"
            )

        if order.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot update another restaurant's order"
            )

        restaurant_allowed = [
            OrderStatus.PREPARING,
            OrderStatus.READY
        ]

        # ACCEPTED is set by assign_delivery_partner().
        if status_data.status not in restaurant_allowed:
            raise HTTPException(
                status_code=403,
                detail="Restaurant can update only to PREPARING or READY"
            )

    # Delivery Partner can update only its assigned orders after READY.
    elif current_user.role == "DELIVERY_PARTNER":

        partner = (
            db.query(DeliveryPartner)
            .filter(DeliveryPartner.user_id == current_user.id)
            .first()
        )

        if partner is None:
            raise HTTPException(
                status_code=404,
                detail="Delivery partner profile not found"
            )

        if order.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=403,
                detail="You can update only orders assigned to you"
            )

        partner_allowed = [
            OrderStatus.PICKED_UP,
            OrderStatus.ON_THE_WAY,
            OrderStatus.DELIVERED
        ]

        if status_data.status not in partner_allowed:
            raise HTTPException(
                status_code=403,
                detail="Delivery partner can update only to PICKED_UP, ON_THE_WAY or DELIVERED"
            )

    order.status = status_data.status

    db.commit()
    db.refresh(order)

    



    return {
        "message": "Order status updated successfully",
        "order": order
    }


# ======================================================
# REVENUE SUMMARY
# ======================================================

# ======================================================
# REVENUE SUMMARY
# ADMIN ONLY
# ======================================================

@router.get("/revenue")
def get_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    orders = db.query(Order).all()

    total_revenue = sum(
        order.total_amount
        for order in orders
    )

    return {
        "total_orders": len(orders),
        "total_revenue": total_revenue
    }


# ======================================================
# REVENUE LEAKAGE
# ADMIN ONLY
# ======================================================

@router.get("/revenue/leakage")
def revenue_leakage(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN")
    )
):
    """
    Detect delivered orders where expected revenue has not been collected.

    Expected revenue = order.total_amount
    Collected revenue = sum of SUCCESS payments for that order
    Leakage = max(expected - collected, 0)

    Orders with zero leakage are excluded.
    """

    delivered_orders = (
        db.query(Order)
        .filter(Order.status == OrderStatus.DELIVERED)
        .all()
    )

    leaked_orders = []
    total_leakage_amount = 0.0

    for order in delivered_orders:
        expected_revenue = float(order.total_amount or 0)

        successful_payments = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id,
                Payment.status == "SUCCESS"
            )
            .all()
        )

        collected_revenue = sum(
            float(payment.amount or 0)
            for payment in successful_payments
        )

        leakage_amount = max(
            round(expected_revenue - collected_revenue, 2),
            0.0
        )

        if leakage_amount > 0:
            leaked_orders.append({
                "id": order.id,
                "customer_id": order.customer_id,
                "restaurant_id": order.restaurant_id,
                "delivery_partner_id": order.delivery_partner_id,
                "status": order.status,
                "created_at": order.created_at,
                "subtotal": order.subtotal,
                "tax": order.tax,
                "delivery_charge": order.delivery_charge,
                "total_amount": order.total_amount,
                "expected_revenue": round(expected_revenue, 2),
                "collected_revenue": round(collected_revenue, 2),
                "leakage_amount": leakage_amount
            })

            total_leakage_amount += leakage_amount

    return {
        "success": True,
        "total_leaked_orders": len(leaked_orders),
        "total_leakage_amount": round(total_leakage_amount, 2),
        "orders": leaked_orders
    }


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "CUSTOMER",
            "RESTAURANT",
            "DELIVERY_PARTNER"
        )
    )
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if current_user.role == "CUSTOMER":

        customer = (
            db.query(Customer)
            .filter(Customer.user_id == current_user.id)
            .first()
        )

        if customer is None or order.customer_id != customer.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    elif current_user.role == "RESTAURANT":

        restaurant = (
            db.query(Restaurant)
            .filter(Restaurant.user_id == current_user.id)
            .first()
        )

        if restaurant is None or order.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    elif current_user.role == "DELIVERY_PARTNER":

        partner = (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.user_id == current_user.id
            )
            .first()
        )

        if partner is None or order.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    return order