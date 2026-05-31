from datetime import date, datetime
from decimal import Decimal

from app.domain.cost_engine import calculate_fixed_costs, calculate_variable_cost
from app.domain.models import CostItem, UsageEvent


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


def test_calculate_fixed_costs_includes_one_time_cost_only_in_matching_month() -> None:
    costs = [
        CostItem(
            id=1,
            name="Recurring server",
            category="Infrastructure",
            cost_type="fixed",
            monthly_amount=Decimal("370"),
            start_date=date(2026, 4, 1),
        ),
        CostItem(
            id=2,
            name="Domain purchase",
            category="Software",
            cost_type="one_time",
            one_time_amount=Decimal("1000"),
            start_date=date(2026, 5, 15),
        ),
    ]

    assert calculate_fixed_costs(costs, date(2026, 5, 1)) == Decimal("1370")
    assert calculate_fixed_costs(costs, date(2026, 6, 1)) == Decimal("370")
