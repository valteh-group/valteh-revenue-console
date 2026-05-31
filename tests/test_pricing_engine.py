from datetime import datetime
from decimal import Decimal

from app.domain.models import PricingPlan, UsageEvent
from app.domain.pricing_engine import recommended_unit_price
from app.domain.revenue_engine import calculate_client_revenue


def test_recommended_unit_price() -> None:
    assert recommended_unit_price(Decimal("8"), Decimal("0.60")) == Decimal("20")


def test_calculate_client_revenue_with_included_usage() -> None:
    plan = PricingPlan(
        id=1,
        name="Professional",
        monthly_fixed_fee=Decimal("1000"),
        included_documents=10,
        price_per_document=Decimal("25"),
    )
    usage = [
        UsageEvent(
            id=1,
            client_id=1,
            service_code="saremi",
            event_type="saremi.document_validation",
            quantity=Decimal("12"),
            unit="document",
            event_timestamp=datetime(2026, 5, 1),
            source_system="test",
        )
    ]
    assert calculate_client_revenue(usage, plan) == Decimal("1050")
