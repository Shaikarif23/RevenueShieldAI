from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.payment import Payment
from app.models.restaurant import Restaurant
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Revenue & Leakage"])


@router.get("/revenue/leakage")
def get_revenue_leakage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return leakage visible to the authenticated user's business scope.

    ADMIN sees the complete portfolio. RESTAURANT, DELIVERY_PARTNER and
    CUSTOMER see only leakage belonging to their own records. This keeps the
    existing ADMIN-only legacy route from producing a 403 for legitimate
    role-specific dashboard users while preserving tenant isolation.
    """
    query = db.query(Order).filter(Order.status == OrderStatus.DELIVERED)

    if current_user.role == "RESTAURANT":
        restaurant = (
            db.query(Restaurant)
            .filter(Restaurant.user_id == current_user.id)
            .first()
        )
        if restaurant is None:
            return {"success": True, "total_leaked_orders": 0, "total_leakage_amount": 0.0, "orders": []}
        query = query.filter(Order.restaurant_id == restaurant.id)

    elif current_user.role == "CUSTOMER":
        customer = (
            db.query(Customer)
            .filter(Customer.user_id == current_user.id)
            .first()
        )
        if customer is None:
            return {"success": True, "total_leaked_orders": 0, "total_leakage_amount": 0.0, "orders": []}
        query = query.filter(Order.customer_id == customer.id)

    elif current_user.role == "DELIVERY_PARTNER":
        partner = (
            db.query(DeliveryPartner)
            .filter(DeliveryPartner.user_id == current_user.id)
            .first()
        )
        if partner is None:
            return {"success": True, "total_leaked_orders": 0, "total_leakage_amount": 0.0, "orders": []}
        query = query.filter(Order.delivery_partner_id == partner.id)

    elif current_user.role != "ADMIN":
        return {"success": True, "total_leaked_orders": 0, "total_leakage_amount": 0.0, "orders": []}

    delivered_orders = query.all()
    leaked_orders = []
    total_leakage_amount = 0.0

    for order in delivered_orders:
        expected = float(order.total_amount or 0)
        successful_payments = (
            db.query(Payment)
            .filter(Payment.order_id == order.id, Payment.status == "SUCCESS")
            .all()
        )
        collected = sum(float(payment.amount or 0) for payment in successful_payments)
        leakage = max(round(expected - collected, 2), 0.0)

        if leakage <= 0:
            continue

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
            "expected_revenue": round(expected, 2),
            "collected_revenue": round(collected, 2),
            "leakage_amount": leakage,
            "leakage_percentage": round((leakage / expected) * 100, 2) if expected else 0.0,
        })
        total_leakage_amount += leakage

    return {
        "success": True,
        "total_leaked_orders": len(leaked_orders),
        "total_leakage_amount": round(total_leakage_amount, 2),
        "orders": leaked_orders,
    }
