
from typing import Dict


def calculate_risk(
    expected_revenue: float,
    collected_revenue: float,
    leakage_amount: float
) -> Dict:

    expected_revenue = float(
        expected_revenue or 0
    )

    collected_revenue = float(
        collected_revenue or 0
    )

    leakage_amount = float(
        leakage_amount or 0
    )

    # ======================================================
    # DATA QUALITY
    # ======================================================

    if expected_revenue <= 0:

        return {
            "risk_score": 0,
            "risk_level": "MEDIUM",
            "risk_reason": "Invalid or zero expected revenue"
        }

    # ======================================================
    # COLLECTION RATIO
    # ======================================================

    collection_ratio = (
        collected_revenue
        / expected_revenue
    )

    # ======================================================
    # LEAKAGE RATIO
    # ======================================================

    leakage_ratio = (
        leakage_amount
        / expected_revenue
    )

    # ======================================================
    # RISK SCORE
    # ======================================================

    risk_score = 0

    # ------------------------------------------------------
    # SIGNAL 1: COLLECTION
    # ------------------------------------------------------

    if collected_revenue == 0:

        risk_score += 60

    elif collection_ratio < 0.50:

        risk_score += 50

    elif collection_ratio < 0.80:

        risk_score += 30

    elif collection_ratio < 1.00:

        risk_score += 15

    # ------------------------------------------------------
    # SIGNAL 2: LEAKAGE SEVERITY
    # ------------------------------------------------------

    if leakage_ratio >= 0.75:

        risk_score += 25

    elif leakage_ratio >= 0.50:

        risk_score += 20

    elif leakage_ratio >= 0.25:

        risk_score += 10

    elif leakage_ratio > 0:

        risk_score += 5

    # ------------------------------------------------------
    # CAP SCORE
    # ------------------------------------------------------

    risk_score = min(
        risk_score,
        100
    )

    # ======================================================
    # RISK LEVEL
    # ======================================================

    if risk_score >= 70:

        risk_level = "HIGH"

    elif risk_score >= 40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    # ======================================================
    # RISK REASON
    # ======================================================

    if collected_revenue == 0:

        risk_reason = (
            "No successful payment collected "
            "for a delivered order"
        )

    elif leakage_ratio >= 0.50:

        risk_reason = (
            "More than 50% of expected revenue "
            "is not collected"
        )

    elif leakage_ratio > 0:

        risk_reason = (
            "Partial revenue collection detected"
        )

    else:

        risk_reason = (
            "Revenue fully collected"
        )

    # ======================================================
    # RESPONSE
    # ======================================================

    return {

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "risk_reason":
            risk_reason
    }
