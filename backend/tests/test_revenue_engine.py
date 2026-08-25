from types import SimpleNamespace

from app.services.revenue_engine import revenue_metrics, order_metrics


def test_full_collection_has_no_leakage():
    result = revenue_metrics(580, 580)
    assert result["leakage_amount"] == 0
    assert result["risk_level"] == "LOW"
    assert result["is_leakage"] is False


def test_zero_collection_is_high_risk():
    result = revenue_metrics(580, 0)
    assert result["leakage_amount"] == 580
    assert result["leakage_percentage"] == 100
    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] == 85


def test_partial_collection_is_detected():
    result = revenue_metrics(580, 300)
    assert result["leakage_amount"] == 280
    assert result["collection_percentage"] == round(300 / 580 * 100, 2)
    assert result["is_leakage"] is True


def test_order_metrics_ignores_failed_payment():
    order = SimpleNamespace(total_amount=580)
    payments = [
        SimpleNamespace(amount=300, status="FAILED"),
        SimpleNamespace(amount=200, status="SUCCESS"),
    ]
    result = order_metrics(order, payments)
    assert result["collected_revenue"] == 200
    assert result["leakage_amount"] == 380
