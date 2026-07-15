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
            cost_key="infrastructure.server",
            name="Recurring server",
            category="Infrastructure",
            cost_type="fixed",
            charge_basis="flat",
            quantity=Decimal("1"),
            unit_cost=Decimal("370"),
            unit="month",
            billing_frequency="monthly",
            start_date=date(2026, 4, 1),
        ),
        CostItem(
            id=2,
            cost_key="software.domain",
            name="Domain purchase",
            category="Software",
            cost_type="one_time",
            charge_basis="flat",
            quantity=Decimal("1"),
            unit_cost=Decimal("1000"),
            unit="payment",
            billing_frequency="once",
            start_date=date(2026, 5, 15),
            end_date=date(2026, 5, 15),
        ),
    ]

    assert calculate_fixed_costs(costs, date(2026, 5, 1)) == Decimal("1370")
    assert calculate_fixed_costs(costs, date(2026, 6, 1)) == Decimal("370")


def test_effective_dated_fixed_cost_versions_preserve_history() -> None:
    common = {
        "cost_key": "software.microsoft365.team",
        "name": "Microsoft 365",
        "category": "Software",
        "cost_type": "fixed",
        "charge_basis": "per_user",
        "unit": "user-month",
        "billing_frequency": "monthly",
    }
    costs = [
        CostItem(
            id=1,
            quantity=Decimal("2"),
            unit_cost=Decimal("200"),
            start_date=date(2026, 5, 1),
            end_date=date(2026, 6, 30),
            **common,
        ),
        CostItem(
            id=2,
            quantity=Decimal("3"),
            unit_cost=Decimal("220"),
            start_date=date(2026, 7, 1),
            **common,
        ),
    ]

    assert calculate_fixed_costs(costs, date(2026, 6, 1)) == Decimal("400")
    assert calculate_fixed_costs(costs, date(2026, 7, 1)) == Decimal("660")


def test_variable_cost_uses_rate_effective_on_event_date() -> None:
    usage = [
        UsageEvent(
            id=1,
            client_id=1,
            service_code="saremi",
            event_type="saremi.document_validation",
            quantity=Decimal("10"),
            unit="document",
            event_timestamp=datetime(2026, 7, 10),
            source_system="test",
        )
    ]
    common = {
        "cost_key": "ai.document_analysis",
        "name": "Document analysis",
        "category": "AI",
        "cost_type": "variable",
        "charge_basis": "usage",
        "quantity": Decimal("1"),
        "unit": "saremi.document_validation",
        "billing_frequency": "usage",
    }
    rates = [
        CostItem(
            id=1,
            unit_cost=Decimal("1"),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 30),
            **common,
        ),
        CostItem(id=2, unit_cost=Decimal("1.20"), start_date=date(2026, 7, 1), **common),
    ]

    assert calculate_variable_cost(usage, rates) == Decimal("12.00")
