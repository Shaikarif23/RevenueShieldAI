from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.payment import Payment
from app.models.payment_status import PaymentStatus
from app.models.user import User
from app.utils.roles import require_role


router = APIRouter(
    prefix="/ai",
    tags=["AI RevenueShield"]
)


# ======================================================
# BUILD ANOMALY
# ======================================================

def build_anomaly(
    order: Order,
    collected: float,
    expected: float,
):
    reasons = []
    score = 0
    anomaly_type = None

    # --------------------------------------------------
    # DATA QUALITY ISSUE
    # --------------------------------------------------

    if order.status == OrderStatus.DELIVERED and expected <= 0:

        reasons.append(
            "Delivered order has zero expected revenue"
        )

        score = 50
        anomaly_type = "DATA_QUALITY"

    # --------------------------------------------------
    # REVENUE LEAKAGE
    # --------------------------------------------------

    elif (
        order.status == OrderStatus.DELIVERED
        and expected > collected
    ):

        reasons.append(
            "Delivered order has unpaid revenue"
        )

        score = 60 if collected == 0 else 40
        anomaly_type = "REVENUE_LEAKAGE"

    # --------------------------------------------------
    # CANCELLED ORDER WITH PAYMENT
    # --------------------------------------------------

    elif (
        order.status == OrderStatus.CANCELLED
        and collected > 0
    ):

        reasons.append(
            "Cancelled order has successful payment"
        )

        score = 70
        anomaly_type = "REVENUE_LEAKAGE"

    # --------------------------------------------------
    # HIGH VALUE ORDER
    # --------------------------------------------------

    if expected >= 1000:

        reasons.append(
            "High-value order"
        )

        score += 20

        if anomaly_type is None:
            anomaly_type = "HIGH_VALUE"

    # --------------------------------------------------
    # NO ANOMALY
    # --------------------------------------------------

    if not reasons:
        return None

    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    risk = "LOW"

    if score >= 70:
        risk = "HIGH"

    elif score >= 40:
        risk = "MEDIUM"

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {
        "order_id": order.id,
        "restaurant_id": order.restaurant_id,
        "status": order.status.value,

        "anomaly_type": anomaly_type,

        "expected_revenue": round(
            expected,
            2
        ),

        "collected_revenue": round(
            collected,
            2
        ),

        "leakage_amount": round(
            max(expected - collected, 0),
            2
        ),

        "risk_score": min(
            score,
            100
        ),

        "risk_level": risk,

        "reasons": reasons
    }


# ======================================================
# AI INSIGHTS
# ======================================================

@router.get("/insights")
def revenue_ai_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    orders = db.query(Order).all()

    anomalies = []

    # ==================================================
    # CHECK EVERY ORDER
    # ==================================================

    for order in orders:

        expected = float(
            order.total_amount or 0
        )

        successful_payments = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id,
                Payment.status == PaymentStatus.SUCCESS
            )
            .all()
        )

        collected = sum(
            float(payment.amount or 0)
            for payment in successful_payments
        )

        anomaly = build_anomaly(
            order=order,
            collected=collected,
            expected=expected
        )

        if anomaly:
            anomalies.append(anomaly)

    # ==================================================
    # ALL ORDERS - REPORTING ONLY
    # ==================================================

    total_expected = sum(
        float(order.total_amount or 0)
        for order in orders
    )

    all_successful_payments = (
        db.query(Payment)
        .filter(
            Payment.status == PaymentStatus.SUCCESS
        )
        .all()
    )

    total_collected = sum(
        float(payment.amount or 0)
        for payment in all_successful_payments
    )

    # ==================================================
    # ACTUAL REVENUE LEAKAGE
    #
    # ONLY DELIVERED ORDERS COUNT
    # ==================================================

    delivered_orders = [
        order
        for order in orders
        if order.status == OrderStatus.DELIVERED
    ]

    delivered_expected = sum(
        float(order.total_amount or 0)
        for order in delivered_orders
    )

    delivered_order_ids = [
        order.id
        for order in delivered_orders
    ]

    delivered_collected = 0.0

    if delivered_order_ids:

        delivered_payments = (
            db.query(Payment)
            .filter(
                Payment.order_id.in_(
                    delivered_order_ids
                ),
                Payment.status == PaymentStatus.SUCCESS
            )
            .all()
        )

        delivered_collected = sum(
            float(payment.amount or 0)
            for payment in delivered_payments
        )

    # ==================================================
    # REAL REVENUE GAP
    # ==================================================

    total_revenue_gap = max(
        round(
            delivered_expected
            - delivered_collected,
            2
        ),
        0
    )

    # ==================================================
    # ANOMALY TYPES
    # ==================================================

    revenue_anomalies = [
        anomaly
        for anomaly in anomalies
        if anomaly["anomaly_type"]
        == "REVENUE_LEAKAGE"
    ]

    data_quality_anomalies = [
        anomaly
        for anomaly in anomalies
        if anomaly["anomaly_type"]
        == "DATA_QUALITY"
    ]

    high_value_anomalies = [
        anomaly
        for anomaly in anomalies
        if anomaly["anomaly_type"]
        == "HIGH_VALUE"
    ]

    # ==================================================
    # RISK COUNTS
    # ==================================================

    high_risk = [
        anomaly
        for anomaly in anomalies
        if anomaly["risk_level"] == "HIGH"
    ]

    medium_risk = [
        anomaly
        for anomaly in anomalies
        if anomaly["risk_level"] == "MEDIUM"
    ]

    low_risk = [
        anomaly
        for anomaly in anomalies
        if anomaly["risk_level"] == "LOW"
    ]

    # ==================================================
    # FINAL RESPONSE
    # ==================================================

    return {
        "success": True,

        "summary": {

            "total_orders": len(
                orders
            ),

            "total_expected_revenue": round(
                total_expected,
                2
            ),

            "total_collected_revenue": round(
                total_collected,
                2
            ),

            # IMPORTANT:
            # This is delivered-order leakage only.
            "total_revenue_gap": total_revenue_gap,

            "total_anomalies": len(
                anomalies
            ),

            "revenue_anomalies": len(
                revenue_anomalies
            ),

            "data_quality_anomalies": len(
                data_quality_anomalies
            ),

            "high_value_anomalies": len(
                high_value_anomalies
            ),

            "high_risk_anomalies": len(
                high_risk
            ),

            "medium_risk_anomalies": len(
                medium_risk
            ),

            "low_risk_anomalies": len(
                low_risk
            )
        },

        "anomalies": anomalies
    }


# ======================================================
# GET ANOMALIES
# ======================================================

@router.get("/anomalies")
def get_revenue_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    orders = db.query(Order).all()

    anomalies = []

    for order in orders:

        expected = float(
            order.total_amount or 0
        )

        successful_payments = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id,
                Payment.status == PaymentStatus.SUCCESS
            )
            .all()
        )

        collected = sum(
            float(payment.amount or 0)
            for payment in successful_payments
        )

        anomaly = build_anomaly(
            order,
            collected,
            expected
        )

        if anomaly:
            anomalies.append(anomaly)

    # Highest risk first
    anomalies.sort(
        key=lambda item: item["risk_score"],
        reverse=True
    )

    return {
        "success": True,

        "total_anomalies": len(
            anomalies
        ),

        "anomalies": anomalies
    }