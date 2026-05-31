from datetime import datetime
from decimal import Decimal

from app.domain.cost_engine import calculate_variable_cost
from app.domain.models import UsageEvent


def test_calculate_variable_cost() -> None:
    usage = [
        UsageEvent(
            id=1,
            client_id=1,
            service_code="saremi",
            event_type="saremi.document_validation",
            quantity=Decimal("10"),
            unit="document",
            event_timestamp=datetime(2026, 5, 1),
            source_system="test",
        ),
        UsageEvent(
            id=2,
            client_id=1,
            service_code="graphos",
            event_type="graphos.query",
            quantity=Decimal("20"),
            unit="query",
            event_timestamp=datetime(2026, 5, 1),
            source_system="test",
        ),
    ]
    rates = {"saremi.document_validation": Decimal("4.5"), "graphos.query": Decimal("1.25")}
    assert calculate_variable_cost(usage, rates) == Decimal("70.00")
