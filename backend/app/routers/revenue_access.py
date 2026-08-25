from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.payment import Payment
from app.models.restaurant import Restaurant
from app.models.user import User
from app.services.revenue_engine import order_metrics

router = APIRouter(prefix="/orders", tags=["Revenue & Leakage"])


def _scope_query(db: Session, user: User):
    query = db.query(Order).filter(Order.status == OrderStatus.DELIVERED)

    if user.role == "ADMIN":
        return query
    if user.role == "RESTAURANT":
        profile = db.query(Restaurant).filter(Restaurant.user_id == user.id).first()
        return query.filter(Order.restaurant_id == profile.id) if profile else query.filter(False)
    if user.role == "CUSTOMER":
        profile = db.query(Customer).filter(Customer.user_id == user.id).first()
        return query.filter(Order.customer_id == profile.id) if profile else query.filter(False)
    if user.role == "DELIVERY_PARTNER":
        profile = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == user.id).first()
        return query.filter(Order.delivery_partner_id == profile.id) if profile else query.filter(False)
    return query.filter(False)


@router.get("/revenue/leakage")
def get_revenue_leakage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return financial leakage only within the authenticated user's scope."""
    orders = _scope_query(db, current_user).all()
    order_ids = [order.id for order in orders]
    payments = (
        db.query(Payment)
        .filter(Payment.order_id.in_(order_ids))
        .all()
        if order_ids else []
    )
    payments_by_order = {}
    for payment in payments:
        payments_by_order.setdefault(payment.order_id, []).append(payment)

    leaked_orders = []
    total_expected = 0.0
    total_collected = 0.0
    total_leakage = 0.0

    for order in orders:
        metrics = order_metrics(order, payments_by_order.get(order.id, []))
        total_expected += metrics["expected_revenue"]
        total_collected += metrics["collected_revenue"]
        total_leakage += metrics["leakage_amount"]
        if not metrics["is_leakage"]:
            continue

        leaked_orders.append({
            "id": order.id,
            "customer_id": order.customer_id,
            "restaurant_id": order.restaurant_id,
            "delivery_partner_id": order.delivery_partner_id,
            "status": order.status,
            "created_at": getattr(order, "created_at", None),
            "subtotal": order.subtotal,
            "tax": order.tax,
            "delivery_charge": order.delivery_charge,
            "total_amount": order.total_amount,
            **metrics,
            "recommended_action": (
                "Investigate payment settlement and reconcile the missing amount"
                if metrics["risk_level"] == "HIGH"
                else "Review payment settlement for the partial collection"
            ),
        })

    leaked_orders.sort(key=lambda item: (-item["risk_score"], -item["leakage_amount"]))
    return {
        "success": True,
        "total_orders_checked": len(orders),
        "total_leaked_orders": len(leaked_orders),
        "total_expected_revenue": round(total_expected, 2),
        "total_collected_revenue": round(total_collected, 2),
        "total_leakage_amount": round(total_leakage, 2),
        "leakage_percentage": round((total_leakage / total_expected) * 100, 2) if total_expected else 0.0,
        "orders": leaked_orders,
    }
