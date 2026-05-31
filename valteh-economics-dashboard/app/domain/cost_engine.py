from __future__ import annotations

from collections.abc import Iterable, Mapping
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


def calculate_fixed_costs(cost_items: Iterable[CostItem]) -> Decimal:
    return sum(
        (money(item.monthly_amount) for item in cost_items if item.active and item.cost_type == "fixed"), Decimal("0")
    )


def _normalize_rates(cost_rates: Mapping[str, Decimal] | Iterable[CostItem]) -> dict[str, Decimal]:
    if isinstance(cost_rates, Mapping):
        return {key: money(value) for key, value in cost_rates.items()}
    rates: dict[str, Decimal] = {}
    for item in cost_rates:
        if item.active and item.cost_type == "variable":
            key = item.unit or item.name
            rates[key] = rates.get(key, Decimal("0")) + money(item.unit_cost)
    return rates
