from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.payment import Payment
from app.models.payment_status import PaymentStatus
from app.models.restaurant import Restaurant
from app.models.user import User
from app.services.revenue_engine import calculate_risk, calculate_recommendation

router = APIRouter(prefix="/ai", tags=["AI RevenueShield"])


def _scoped_orders(db: Session, user: User):
    query = db.query(Order)
    if user.role == "ADMIN":
        return query.all()
    if user.role == "RESTAURANT":
        owner = db.query(Restaurant).filter(Restaurant.user_id == user.id).first()
        return query.filter(Order.restaurant_id == owner.id).all() if owner else []
    if user.role == "CUSTOMER":
        customer = db.query(Customer).filter(Customer.user_id == user.id).first()
        return query.filter(Order.customer_id == customer.id).all() if customer else []
    if user.role == "DELIVERY_PARTNER":
        partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == user.id).first()
        return query.filter(Order.delivery_partner_id == partner.id).all() if partner else []
    return []


def _payment_totals(db: Session, order_ids):
    if not order_ids:
        return {}
    payments = db.query(Payment).filter(
        Payment.order_id.in_(order_ids),
        Payment.status == PaymentStatus.SUCCESS,
    ).all()
    totals = {}
    for payment in payments:
        totals[payment.order_id] = totals.get(payment.order_id, 0.0) + float(payment.amount or 0)
    return totals


def _anomaly(order: Order, collected: float):
    expected = round(float(order.total_amount or 0), 2)
    collected = round(float(collected or 0), 2)

    if order.status == OrderStatus.DELIVERED and expected <= 0:
        return {
            "order_id": order.id,
            "restaurant_id": order.restaurant_id,
            "status": order.status.value,
            "anomaly_type": "DATA_QUALITY",
            "expected_revenue": expected,
            "collected_revenue": collected,
            "leakage_amount": 0.0,
            "risk_score": 0,
            "risk_level": "MEDIUM",
            "risk_reason": "Delivered order has zero or invalid expected revenue",
            "recommendation": "Review order pricing and item data.",
        }

    if order.status == OrderStatus.CANCELLED and collected > 0:
        return {
            "order_id": order.id,
            "restaurant_id": order.restaurant_id,
            "status": order.status.value,
            "anomaly_type": "CANCELLED_WITH_PAYMENT",
            "expected_revenue": expected,
            "collected_revenue": collected,
            "leakage_amount": 0.0,
            "risk_score": 70,
            "risk_level": "HIGH",
            "risk_reason": "Cancelled order has successful payment",
            "recommendation": "Verify refund or settlement status.",
        }

    if order.status != OrderStatus.DELIVERED or expected <= collected:
        return None

    leakage = round(expected - collected, 2)
    risk = calculate_risk(expected, collected)
    return {
        "order_id": order.id,
        "restaurant_id": order.restaurant_id,
        "status": order.status.value,
        "anomaly_type": "REVENUE_LEAKAGE",
        "expected_revenue": expected,
        "collected_revenue": collected,
        "leakage_amount": leakage,
        "leakage_percentage": round((leakage / expected) * 100, 2),
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "risk_reason": risk["risk_reason"],
        "recommendation": calculate_recommendation(risk["risk_level"], leakage),
    }


def _build_response(db: Session, user: User):
    orders = _scoped_orders(db, user)
    totals = _payment_totals(db, [o.id for o in orders])
    anomalies = []

    for order in orders:
        item = _anomaly(order, totals.get(order.id, 0.0))
        if item:
            anomalies.append(item)

    delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
    expected = round(sum(float(o.total_amount or 0) for o in delivered), 2)
    collected = round(sum(totals.get(o.id, 0.0) for o in delivered), 2)
    leakage = max(round(expected - collected, 2), 0.0)

    return {
        "success": True,
        "summary": {
            "total_orders": len(orders),
            "delivered_orders": len(delivered),
            "expected_revenue": expected,
            "collected_revenue": collected,
            "revenue_leakage": leakage,
            "leakage_percentage": round((leakage / expected) * 100, 2) if expected else 0.0,
            "total_anomalies": len(anomalies),
            "high_risk_anomalies": sum(a["risk_level"] == "HIGH" for a in anomalies),
            "medium_risk_anomalies": sum(a["risk_level"] == "MEDIUM" for a in anomalies),
            "low_risk_anomalies": sum(a["risk_level"] == "LOW" for a in anomalies),
        },
        "anomalies": sorted(anomalies, key=lambda x: (x["risk_score"], x["leakage_amount"]), reverse=True),
    }


@router.get("/insights")
def revenue_ai_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _build_response(db, current_user)


@router.get("/anomalies")
def get_revenue_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = _build_response(db, current_user)
    return {
        "success": True,
        "total_anomalies": len(result["anomalies"]),
        "anomalies": result["anomalies"],
    }
