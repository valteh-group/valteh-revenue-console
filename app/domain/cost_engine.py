from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.domain.models import CostItem, UsageEvent
from app.domain.unit_economics import money


def calculate_variable_cost(
    usage_events: Iterable[UsageEvent],
    cost_rates: Mapping[str, Decimal] | Iterable[CostItem],
) -> Decimal:
    """Calculate variable cost by multiplying event quantity by matching unit rate."""

    total = Decimal("0")
    for event in usage_events:
        rates = _normalize_rates(cost_rates, event.event_timestamp)
        rate = rates.get(event.event_type, Decimal("0"))
        total += money(event.quantity) * money(rate)
    return total


def calculate_fixed_costs(cost_items: Iterable[CostItem], month: date | None = None) -> Decimal:
    month = month or date.today().replace(day=1)
    return sum(
        (
            _fixed_cost_for_month(item, month)
            for item in cost_items
            if item.cost_type in {"fixed", "one_time"}
        ),
        Decimal("0"),
    )


def _fixed_cost_for_month(item: CostItem, month: date) -> Decimal:
    if not is_cost_effective(item, month, month_scope=True):
        return Decimal("0")
    if item.cost_type == "fixed":
        if item.billing_frequency == "monthly":
            charge_date = _charge_date(item, month)
            return money(item.configured_amount) if _is_cost_effective_on_day(item, charge_date) else Decimal("0")
        if item.billing_frequency == "annual" and item.start_date and item.start_date.month == month.month:
            charge_date = _charge_date(item, month)
            return money(item.configured_amount) if _is_cost_effective_on_day(item, charge_date) else Decimal("0")
    if item.cost_type == "one_time" and item.start_date:
        if item.start_date.year == month.year and item.start_date.month == month.month:
            return money(item.configured_amount)
    return Decimal("0")


def is_cost_effective(item: CostItem, when: date | datetime, *, month_scope: bool = False) -> bool:
    """Return whether an actual cost version applies on a date.

    By default the exact day is used. Month-level calculations can explicitly
    request overlap semantics with ``month_scope=True``.
    """

    when_date = when.date() if isinstance(when, datetime) else when
    period_end = when_date
    if month_scope:
        next_month = (when_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        period_end = next_month - timedelta(days=1)
    return _is_cost_effective_on_day(item, when_date, period_end)


def _is_cost_effective_on_day(item: CostItem, when: date, period_end: date | None = None) -> bool:
    period_end = period_end or when
    return (
        item.enabled
        and item.record_type == "actual"
        and (item.start_date is None or item.start_date <= period_end)
        and (item.end_date is None or item.end_date >= when)
    )


def _charge_date(item: CostItem, month: date) -> date:
    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = (next_month - timedelta(days=1)).day
    day = item.charge_day or (item.start_date.day if item.start_date else 1)
    return month.replace(day=min(day, last_day))


def _normalize_rates(
    cost_rates: Mapping[str, Decimal] | Iterable[CostItem],
    when: date | datetime,
) -> dict[str, Decimal]:
    if isinstance(cost_rates, Mapping):
        return {key: money(value) for key, value in cost_rates.items()}
    rates: dict[str, Decimal] = {}
    for item in cost_rates:
        if item.cost_type == "variable" and is_cost_effective(item, when):
            key = item.unit
            rates[key] = rates.get(key, Decimal("0")) + money(item.unit_cost)
    return rates
