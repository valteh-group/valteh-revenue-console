from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from decimal import Decimal

from app.domain.models import CostItem, UsageEvent
from app.domain.unit_economics import money


def calculate_variable_cost(
    usage_events: Iterable[UsageEvent],
    cost_rates: Mapping[str, Decimal] | Iterable[CostItem],
) -> Decimal:
    """Calculate variable cost by multiplying event quantity by matching unit rate."""

    rates = _normalize_rates(cost_rates)
    total = Decimal("0")
    for event in usage_events:
        rate = rates.get(event.event_type, Decimal("0"))
        total += money(event.quantity) * money(rate)
    return total


def calculate_fixed_costs(cost_items: Iterable[CostItem], month: date | None = None) -> Decimal:
    return sum(
        (
            _fixed_cost_for_month(item, month)
            for item in cost_items
            if item.active and item.cost_type in {"fixed", "one_time"}
        ),
        Decimal("0"),
    )


def _fixed_cost_for_month(item: CostItem, month: date | None) -> Decimal:
    if item.cost_type == "fixed":
        if month is None or item.start_date is None or item.start_date <= month:
            return money(item.monthly_amount)
        return Decimal("0")
    if item.cost_type == "one_time" and month and item.start_date:
        if item.start_date.year == month.year and item.start_date.month == month.month:
            return money(item.one_time_amount)
    return Decimal("0")


def _normalize_rates(cost_rates: Mapping[str, Decimal] | Iterable[CostItem]) -> dict[str, Decimal]:
    if isinstance(cost_rates, Mapping):
        return {key: money(value) for key, value in cost_rates.items()}
    rates: dict[str, Decimal] = {}
    for item in cost_rates:
        if item.active and item.cost_type == "variable":
            key = item.unit or item.name
            rates[key] = rates.get(key, Decimal("0")) + money(item.unit_cost)
    return rates
