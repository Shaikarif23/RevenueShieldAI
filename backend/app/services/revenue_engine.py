from __future__ import annotations

from typing import Iterable

from app.models.payment_status import PaymentStatus


SUCCESS_STATUSES = {PaymentStatus.SUCCESS, "SUCCESS"}


def successful_amount(payments: Iterable) -> float:
    return round(
        sum(
            float(payment.amount or 0)
            for payment in payments
            if payment.status in SUCCESS_STATUSES
        ),
        2,
    )


def revenue_metrics(expected: float, collected: float) -> dict:
    expected = round(max(float(expected or 0), 0), 2)
    collected = round(max(float(collected or 0), 0), 2)

    leakage = round(max(expected - collected, 0), 2)
    over_collection = round(max(collected - expected, 0), 2)
    leakage_percentage = round((leakage / expected) * 100, 2) if expected else 0.0
    collection_percentage = round((collected / expected) * 100, 2) if expected else 0.0

    if expected <= 0:
        risk_score = 0
        risk_level = "MEDIUM"
        risk_reason = "Expected revenue is zero or invalid"
    elif leakage <= 0:
        risk_score = 0
        risk_level = "LOW"
        risk_reason = "Expected revenue fully collected"
    elif collected <= 0:
        risk_score = 85
        risk_level = "HIGH"
        risk_reason = "No successful payment collected"
    elif leakage_percentage >= 50:
        risk_score = 75
        risk_level = "HIGH"
        risk_reason = "More than half of expected revenue is missing"
    elif leakage_percentage >= 10:
        risk_score = 60
        risk_level = "MEDIUM"
        risk_reason = "Partial revenue collection detected"
    else:
        risk_score = 40
        risk_level = "LOW"
        risk_reason = "Small revenue difference detected"

    return {
        "expected_revenue": expected,
        "collected_revenue": collected,
        "leakage_amount": leakage,
        "leakage_percentage": leakage_percentage,
        "collection_percentage": collection_percentage,
        "over_collection_amount": over_collection,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "is_leakage": leakage > 0,
    }


def order_metrics(order, payments: Iterable) -> dict:
    return revenue_metrics(
        float(order.total_amount or 0),
        successful_amount(payments),
    )
