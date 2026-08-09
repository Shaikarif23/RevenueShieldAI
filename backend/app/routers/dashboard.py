
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.order import Order
from app.models.order_status import OrderStatus

from app.models.payment import Payment
from app.models.payment_status import PaymentStatus

from app.models.restaurant import Restaurant
from app.models.user import User

from app.utils.roles import require_role


router = APIRouter(
    prefix="/dashboard",
    tags=["RevenueShield Dashboard"]
)


# ==========================================================
# COMMON HELPERS
# ==========================================================

ALLOWED_RISK_LEVELS = {
    "HIGH",
    "MEDIUM",
    "LOW"
}


def validate_restaurant(
    db: Session,
    restaurant_id: Optional[int]
):
    """
    Validate restaurant_id when supplied.
    """

    if restaurant_id is None:
        return None

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return restaurant


def validate_filters(
    db: Session,
    restaurant_id: Optional[int],
    from_date: Optional[date],
    to_date: Optional[date],
    risk_level: Optional[str] = None
):
    """
    Validate all dashboard filters.
    """

    restaurant = validate_restaurant(
        db,
        restaurant_id
    )

    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="from_date cannot be later than to_date"
        )

    if risk_level is not None:

        risk_level = risk_level.upper()

        if risk_level not in ALLOWED_RISK_LEVELS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid risk_level. "
                    "Allowed values: HIGH, MEDIUM, LOW"
                )
            )

    return restaurant


def get_order_date(order):
    """
    Safely find the date field used by the Order model.

    Supports common field names without assuming one specific
    schema.
    """

    possible_fields = [
        "created_at",
        "order_date",
        "created_on",
        "date"
    ]

    for field in possible_fields:

        if hasattr(order, field):

            value = getattr(
                order,
                field,
                None
            )

            if value is not None:
                return value

    return None


def order_matches_date_filter(
    order,
    from_date: Optional[date],
    to_date: Optional[date]
):
    """
    Apply date filtering safely.

    If no date filter is supplied, the order is accepted.

    If a date filter is supplied but the Order model has no
    supported date field, the order is excluded.
    """

    if from_date is None and to_date is None:
        return True

    order_date = get_order_date(order)

    if order_date is None:
        return False

    if isinstance(order_date, datetime):
        order_date_only = order_date.date()
    elif isinstance(order_date, date):
        order_date_only = order_date
    else:
        return False

    if from_date and order_date_only < from_date:
        return False

    if to_date and order_date_only > to_date:
        return False

    return True


def build_filters_response(
    restaurant_id: Optional[int],
    from_date: Optional[date],
    to_date: Optional[date],
    risk_level: Optional[str] = None
):
    response = {
        "restaurant_id": restaurant_id,
        "from_date": (
            from_date.isoformat()
            if from_date
            else None
        ),
        "to_date": (
            to_date.isoformat()
            if to_date
            else None
        )
    }

    if risk_level is not None:
        response["risk_level"] = risk_level.upper()

    return response


def get_restaurant_map(
    db: Session,
    restaurant_ids
):
    """
    Fetch all required restaurants in one query.
    """

    if not restaurant_ids:
        return {}

    restaurants = (
        db.query(Restaurant)
        .filter(
            Restaurant.id.in_(restaurant_ids)
        )
        .all()
    )

    return {
        restaurant.id: restaurant
        for restaurant in restaurants
    }


def get_payment_totals(
    db: Session,
    order_ids
):
    """
    Fetch successful payments once instead of querying the
    Payment table separately for every order.

    Returns:
        {
            order_id: total_successful_payment
        }
    """

    if not order_ids:
        return {}

    payments = (
        db.query(Payment)
        .filter(
            Payment.order_id.in_(order_ids),
            Payment.status == PaymentStatus.SUCCESS
        )
        .all()
    )

    payment_totals = {}

    for payment in payments:

        order_id = payment.order_id

        payment_totals.setdefault(
            order_id,
            0.0
        )

        payment_totals[order_id] += float(
            payment.amount or 0
        )

    return payment_totals


def calculate_risk(
    expected: float,
    collected: float
):
    """
    Revenue leakage risk calculation.

    Current business rule:

    No successful payment for a delivered order
        -> HIGH / 85

    Partial payment
        -> MEDIUM / 60

    Small remaining difference
        -> LOW / 40
    """

    if expected <= 0:
        return {
            "risk_score": 0,
            "risk_level": "MEDIUM",
            "risk_reason": (
                "Invalid or zero expected revenue"
            )
        }

    if collected <= 0:

        return {
            "risk_score": 85,
            "risk_level": "HIGH",
            "risk_reason": (
                "No successful payment collected "
                "for a delivered order"
            )
        }

    if collected < expected:

        return {
            "risk_score": 60,
            "risk_level": "MEDIUM",
            "risk_reason": (
                "Collected revenue is lower "
                "than expected revenue"
            )
        }

    return {
        "risk_score": 0,
        "risk_level": "LOW",
        "risk_reason": "No revenue leakage detected"
    }


def build_anomalies(
    delivered_orders,
    payment_totals,
    restaurants
):
    """
    Build revenue leakage and data-quality anomalies.
    """

    anomalies = []

    for order in delivered_orders:

        expected = round(
            float(order.total_amount or 0),
            2
        )

        collected = round(
            float(
                payment_totals.get(
                    order.id,
                    0.0
                )
            ),
            2
        )

        restaurant = restaurants.get(
            order.restaurant_id
        )

        restaurant_name = (
            restaurant.restaurant_name
            if restaurant
            else "Unknown Restaurant"
        )

        # ==================================================
        # DATA QUALITY
        # ==================================================

        if expected <= 0:

            anomalies.append({
                "order_id": order.id,
                "restaurant_id": order.restaurant_id,
                "restaurant_name": restaurant_name,
                "anomaly_type": "DATA_QUALITY",
                "expected_revenue": 0,
                "collected_revenue": collected,
                "leakage_amount": 0,
                "risk_score": 0,
                "risk_level": "MEDIUM",
                "risk_reason": (
                    "Invalid or zero expected revenue"
                )
            })

            continue

        # ==================================================
        # REVENUE LEAKAGE
        # ==================================================

        if expected > collected:

            leakage = round(
                expected - collected,
                2
            )

            risk = calculate_risk(
                expected,
                collected
            )

            anomalies.append({
                "order_id": order.id,
                "restaurant_id": order.restaurant_id,
                "restaurant_name": restaurant_name,
                "anomaly_type": "REVENUE_LEAKAGE",
                "expected_revenue": expected,
                "collected_revenue": collected,
                "leakage_amount": leakage,
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"],
                "risk_reason": risk["risk_reason"]
            })

    # Highest leakage first
    anomalies.sort(
        key=lambda item: item["leakage_amount"],
        reverse=True
    )

    return anomalies


def filter_anomalies(
    anomalies,
    risk_level: Optional[str]
):
    if risk_level is None:
        return anomalies

    risk_level = risk_level.upper()

    return [
        anomaly
        for anomaly in anomalies
        if anomaly["risk_level"] == risk_level
    ]


def calculate_summary(
    all_orders,
    delivered_orders,
    payment_totals
):
    """
    Calculate the core RevenueShield metrics.
    """

    total_orders = len(all_orders)

    total_expected_revenue = round(
        sum(
            float(order.total_amount or 0)
            for order in all_orders
        ),
        2
    )

    total_collected_revenue = round(
        sum(
            payment_totals.get(
                order.id,
                0.0
            )
            for order in all_orders
        ),
        2
    )

    delivered_expected_revenue = round(
        sum(
            float(order.total_amount or 0)
            for order in delivered_orders
        ),
        2
    )

    delivered_collected_revenue = round(
        sum(
            payment_totals.get(
                order.id,
                0.0
            )
            for order in delivered_orders
        ),
        2
    )

    total_leakage = max(
        round(
            delivered_expected_revenue
            - delivered_collected_revenue,
            2
        ),
        0
    )

    if delivered_expected_revenue > 0:

        leakage_percentage = round(
            (
                total_leakage
                / delivered_expected_revenue
            ) * 100,
            2
        )

    else:

        leakage_percentage = 0

    return {
        "total_orders": total_orders,
        "total_expected_revenue": total_expected_revenue,
        "total_collected_revenue": total_collected_revenue,
        "delivered_expected_revenue":
            delivered_expected_revenue,
        "delivered_collected_revenue":
            delivered_collected_revenue,
        "total_leakage": total_leakage,
        "leakage_percentage":
            leakage_percentage
    }


def calculate_risk_summary(
    anomalies
):
    revenue_leakage_anomalies = sum(
        1
        for item in anomalies
        if item["anomaly_type"]
        == "REVENUE_LEAKAGE"
    )

    data_quality_anomalies = sum(
        1
        for item in anomalies
        if item["anomaly_type"]
        == "DATA_QUALITY"
    )

    high_risk = sum(
        1
        for item in anomalies
        if item["risk_level"] == "HIGH"
    )

    medium_risk = sum(
        1
        for item in anomalies
        if item["risk_level"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for item in anomalies
        if item["risk_level"] == "LOW"
    )

    return {
        "revenue_leakage_anomalies":
            revenue_leakage_anomalies,

        "data_quality_anomalies":
            data_quality_anomalies,

        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk
    }


def build_restaurant_leakage(
    delivered_orders,
    payment_totals,
    restaurants
):
    """
    Calculate restaurant-wise leakage.
    """

    restaurant_data = {}

    for order in delivered_orders:

        restaurant_id = order.restaurant_id

        if restaurant_id not in restaurant_data:

            restaurant_data[restaurant_id] = {
                "restaurant_id": restaurant_id,
                "delivered_orders": 0,
                "expected_revenue": 0.0,
                "collected_revenue": 0.0
            }

        restaurant_data[
            restaurant_id
        ]["delivered_orders"] += 1

        restaurant_data[
            restaurant_id
        ]["expected_revenue"] += float(
            order.total_amount or 0
        )

        restaurant_data[
            restaurant_id
        ]["collected_revenue"] += float(
            payment_totals.get(
                order.id,
                0.0
            )
        )

    results = []

    for restaurant_id, data in restaurant_data.items():

        restaurant = restaurants.get(
            restaurant_id
        )

        expected = round(
            data["expected_revenue"],
            2
        )

        collected = round(
            data["collected_revenue"],
            2
        )

        leakage = max(
            round(
                expected - collected,
                2
            ),
            0
        )

        if expected > 0:

            leakage_percentage = round(
                (
                    leakage
                    / expected
                ) * 100,
                2
            )

        else:

            leakage_percentage = 0

        results.append({
            "restaurant_id": restaurant_id,

            "restaurant_name": (
                restaurant.restaurant_name
                if restaurant
                else "Unknown Restaurant"
            ),

            "address": (
                restaurant.address
                if restaurant
                else None
            ),

            "rating": (
                restaurant.rating
                if restaurant
                else None
            ),

            "delivered_orders":
                data["delivered_orders"],

            "expected_revenue":
                expected,

            "collected_revenue":
                collected,

            "leakage_amount":
                leakage,

            "leakage_percentage":
                leakage_percentage
        })

    results.sort(
        key=lambda item: item["leakage_amount"],
        reverse=True
    )

    return results


def build_alerts(
    anomalies
):
    """
    Convert anomalies into actionable alerts.
    """

    alerts = []

    for anomaly in anomalies:

        if anomaly["anomaly_type"] == "REVENUE_LEAKAGE":

            if anomaly["risk_level"] == "HIGH":
                priority = "CRITICAL"

            elif anomaly["risk_level"] == "MEDIUM":
                priority = "HIGH"

            else:
                priority = "MEDIUM"

            message = (
                f"Order #{anomaly['order_id']} "
                f"has ₹{float(anomaly['leakage_amount'])} "
                f"revenue leakage."
            )

            recommendation = (
                "Immediately investigate payment settlement "
                "for this delivered order and verify whether "
                "the restaurant received the expected payment."
            )

            alerts.append({
                "alert_type":
                    "REVENUE_LEAKAGE",

                "priority":
                    priority,

                "order_id":
                    anomaly["order_id"],

                "restaurant_id":
                    anomaly["restaurant_id"],

                "restaurant_name":
                    anomaly["restaurant_name"],

                "leakage_amount":
                    anomaly["leakage_amount"],

                "risk_score":
                    anomaly["risk_score"],

                "risk_level":
                    anomaly["risk_level"],

                "message":
                    message,

                "recommendation":
                    recommendation
            })

        elif anomaly["anomaly_type"] == "DATA_QUALITY":

            alerts.append({
                "alert_type":
                    "DATA_QUALITY",

                "priority":
                    "MEDIUM",

                "order_id":
                    anomaly["order_id"],

                "restaurant_id":
                    anomaly["restaurant_id"],

                "restaurant_name":
                    anomaly["restaurant_name"],

                "leakage_amount":
                    0,

                "risk_score":
                    anomaly["risk_score"],

                "risk_level":
                    anomaly["risk_level"],

                "message": (
                    f"Order #{anomaly['order_id']} "
                    "contains invalid expected revenue."
                ),

                "recommendation": (
                    "Review the order amount and correct "
                    "the underlying order data."
                )
            })

    # Critical first, then High, then Medium
    priority_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2
    }

    alerts.sort(
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99
            ),
            -float(
                item["leakage_amount"]
            )
        )
    )

    return alerts


def get_dashboard_data(
    db: Session,
    restaurant_id: Optional[int],
    from_date: Optional[date],
    to_date: Optional[date]
):
    """
    Centralized data loading.

    This avoids repeating database queries across endpoints.
    """

    validate_filters(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    # ======================================================
    # GET ORDERS
    # ======================================================

    orders = (
        db.query(Order)
        .all()
    )

    # Apply filters in Python so this remains compatible with
    # the current Order model regardless of the exact date field.
    filtered_orders = [
        order
        for order in orders
        if (
            restaurant_id is None
            or order.restaurant_id == restaurant_id
        )
        and order_matches_date_filter(
            order,
            from_date,
            to_date
        )
    ]

    # ======================================================
    # DELIVERED ORDERS
    # ======================================================

    delivered_orders = [
        order
        for order in filtered_orders
        if order.status == OrderStatus.DELIVERED
    ]

    # ======================================================
    # PAYMENT TOTALS
    # ======================================================

    order_ids = [
        order.id
        for order in filtered_orders
    ]

    payment_totals = get_payment_totals(
        db,
        order_ids
    )

    # ======================================================
    # RESTAURANTS
    # ======================================================

    restaurant_ids = {
        order.restaurant_id
        for order in filtered_orders
        if order.restaurant_id is not None
    }

    restaurants = get_restaurant_map(
        db,
        restaurant_ids
    )

    return (
        filtered_orders,
        delivered_orders,
        payment_totals,
        restaurants
    )


# ==========================================================
# 1. REVENUE DASHBOARD
# ==========================================================

@router.get("/revenue")
def revenue_dashboard(
    restaurant_id: Optional[int] = Query(
        None,
        description="Filter by restaurant ID"
    ),

    from_date: Optional[date] = Query(
        None,
        description="Start date YYYY-MM-DD"
    ),

    to_date: Optional[date] = Query(
        None,
        description="End date YYYY-MM-DD"
    ),

    risk_level: Optional[str] = Query(
        None,
        description="HIGH, MEDIUM or LOW"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    validate_filters(
        db,
        restaurant_id,
        from_date,
        to_date,
        risk_level
    )

    (
        orders,
        delivered_orders,
        payment_totals,
        restaurants
    ) = get_dashboard_data(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    summary = calculate_summary(
        orders,
        delivered_orders,
        payment_totals
    )

    anomalies = build_anomalies(
        delivered_orders,
        payment_totals,
        restaurants
    )

    anomalies = filter_anomalies(
        anomalies,
        risk_level
    )

    risk_summary = calculate_risk_summary(
        anomalies
    )

    top_leaked_orders = [
        anomaly
        for anomaly in anomalies
        if anomaly["anomaly_type"]
        == "REVENUE_LEAKAGE"
    ][:5]

    return {
        "success": True,

        "summary": {
            **summary,

            "revenue_anomalies":
                risk_summary[
                    "revenue_leakage_anomalies"
                ],

            "data_quality_anomalies":
                risk_summary[
                    "data_quality_anomalies"
                ],

            "high_risk_anomalies":
                risk_summary["high_risk"],

            "medium_risk_anomalies":
                risk_summary["medium_risk"],

            "low_risk_anomalies":
                risk_summary["low_risk"]
        },

        "filters": build_filters_response(
            restaurant_id,
            from_date,
            to_date,
            risk_level
        ),

        "top_leaked_orders":
            top_leaked_orders
    }


# ==========================================================
# 2. RESTAURANT-WISE LEAKAGE
# ==========================================================

@router.get("/restaurant-leakage")
def restaurant_leakage_dashboard(
    restaurant_id: Optional[int] = Query(
        None,
        description="Filter by restaurant ID"
    ),

    from_date: Optional[date] = Query(
        None,
        description="Start date YYYY-MM-DD"
    ),

    to_date: Optional[date] = Query(
        None,
        description="End date YYYY-MM-DD"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    (
        orders,
        delivered_orders,
        payment_totals,
        restaurants
    ) = get_dashboard_data(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    restaurant_leakage = (
        build_restaurant_leakage(
            delivered_orders,
            payment_totals,
            restaurants
        )
    )

    return {
        "success": True,

        "filters": build_filters_response(
            restaurant_id,
            from_date,
            to_date
        ),

        "total_restaurants":
            len(restaurant_leakage),

        "restaurants":
            restaurant_leakage
    }


# ==========================================================
# 3. ANOMALIES
# ==========================================================

@router.get("/anomalies")
def dashboard_anomalies(
    restaurant_id: Optional[int] = Query(
        None,
        description="Filter by restaurant ID"
    ),

    from_date: Optional[date] = Query(
        None,
        description="Start date YYYY-MM-DD"
    ),

    to_date: Optional[date] = Query(
        None,
        description="End date YYYY-MM-DD"
    ),

    risk_level: Optional[str] = Query(
        None,
        description="HIGH, MEDIUM or LOW"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    validate_filters(
        db,
        restaurant_id,
        from_date,
        to_date,
        risk_level
    )

    (
        orders,
        delivered_orders,
        payment_totals,
        restaurants
    ) = get_dashboard_data(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    anomalies = build_anomalies(
        delivered_orders,
        payment_totals,
        restaurants
    )

    anomalies = filter_anomalies(
        anomalies,
        risk_level
    )

    revenue_leakage_count = sum(
        1
        for item in anomalies
        if item["anomaly_type"]
        == "REVENUE_LEAKAGE"
    )

    data_quality_count = sum(
        1
        for item in anomalies
        if item["anomaly_type"]
        == "DATA_QUALITY"
    )

    return {
        "success": True,

        "filters": build_filters_response(
            restaurant_id,
            from_date,
            to_date,
            risk_level
        ),

        "total_anomalies":
            len(anomalies),

        "revenue_leakage_anomalies":
            revenue_leakage_count,

        "data_quality_anomalies":
            data_quality_count,

        "anomalies":
            anomalies
    }


# ==========================================================
# 4. COMPLETE DASHBOARD OVERVIEW
# ==========================================================

@router.get("/overview")
def dashboard_overview(
    restaurant_id: Optional[int] = Query(
        None,
        description="Filter by restaurant ID"
    ),

    from_date: Optional[date] = Query(
        None,
        description="Start date YYYY-MM-DD"
    ),

    to_date: Optional[date] = Query(
        None,
        description="End date YYYY-MM-DD"
    ),

    risk_level: Optional[str] = Query(
        None,
        description="HIGH, MEDIUM or LOW"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    validate_filters(
        db,
        restaurant_id,
        from_date,
        to_date,
        risk_level
    )

    (
        orders,
        delivered_orders,
        payment_totals,
        restaurants
    ) = get_dashboard_data(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    # ======================================================
    # SUMMARY
    # ======================================================

    summary = calculate_summary(
        orders,
        delivered_orders,
        payment_totals
    )

    # ======================================================
    # ANOMALIES
    # ======================================================

    all_anomalies = build_anomalies(
        delivered_orders,
        payment_totals,
        restaurants
    )

    anomalies = filter_anomalies(
        all_anomalies,
        risk_level
    )

    risk_summary = calculate_risk_summary(
        anomalies
    )

    # ======================================================
    # TOP LEAKED ORDERS
    # ======================================================

    top_leaked_orders = [
        item
        for item in anomalies
        if item["anomaly_type"]
        == "REVENUE_LEAKAGE"
    ][:5]

    # ======================================================
    # RESTAURANT LEAKAGE
    # ======================================================

    restaurant_leakage = (
        build_restaurant_leakage(
            delivered_orders,
            payment_totals,
            restaurants
        )
    )

    # ======================================================
    # RECENT ANOMALIES
    # ======================================================

    recent_anomalies = anomalies[:10]

    return {
        "success": True,

        "filters": build_filters_response(
            restaurant_id,
            from_date,
            to_date,
            risk_level
        ),

        "summary":
            summary,

        "risk_summary":
            risk_summary,

        "top_leaked_orders":
            top_leaked_orders,

        "restaurant_leakage":
            restaurant_leakage,

        "recent_anomalies":
            recent_anomalies
    }


# ==========================================================
# 5. ALERTS & RECOMMENDATIONS
# ==========================================================

@router.get("/alerts")
def dashboard_alerts(
    restaurant_id: Optional[int] = Query(
        None,
        description="Filter by restaurant ID"
    ),

    from_date: Optional[date] = Query(
        None,
        description="Start date YYYY-MM-DD"
    ),

    to_date: Optional[date] = Query(
        None,
        description="End date YYYY-MM-DD"
    ),

    risk_level: Optional[str] = Query(
        None,
        description="HIGH, MEDIUM or LOW"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("ADMIN")
    )
):

    validate_filters(
        db,
        restaurant_id,
        from_date,
        to_date,
        risk_level
    )

    (
        orders,
        delivered_orders,
        payment_totals,
        restaurants
    ) = get_dashboard_data(
        db,
        restaurant_id,
        from_date,
        to_date
    )

    anomalies = build_anomalies(
        delivered_orders,
        payment_totals,
        restaurants
    )

    anomalies = filter_anomalies(
        anomalies,
        risk_level
    )

    alerts = build_alerts(
        anomalies
    )

    critical_alerts = sum(
        1
        for alert in alerts
        if alert["priority"] == "CRITICAL"
    )

    high_alerts = sum(
        1
        for alert in alerts
        if alert["priority"] == "HIGH"
    )

    medium_alerts = sum(
        1
        for alert in alerts
        if alert["priority"] == "MEDIUM"
    )

    return {
        "success": True,

        "filters": build_filters_response(
            restaurant_id,
            from_date,
            to_date,
            risk_level
        ),

        "total_alerts":
            len(alerts),

        "critical_alerts":
            critical_alerts,

        "high_alerts":
            high_alerts,

        "medium_alerts":
            medium_alerts,

        "alerts":
            alerts
    }
