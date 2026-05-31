from __future__ import annotations

from decimal import Decimal

from app.domain.unit_economics import (
    calculate_break_even_clients,
    calculate_break_even_usage,
    calculate_minimum_unit_price,
)


def recommended_unit_price(unit_variable_cost: Decimal, target_margin: Decimal) -> Decimal:
    return calculate_minimum_unit_price(unit_variable_cost, target_margin)


def pricing_summary(
    fixed_costs: Decimal,
    average_margin_per_client: Decimal,
    unit_price: Decimal,
    unit_variable_cost: Decimal,
) -> dict[str, Decimal | int]:
    return {
        "break_even_clients": calculate_break_even_clients(fixed_costs, average_margin_per_client),
        "break_even_usage": calculate_break_even_usage(fixed_costs, unit_price, unit_variable_cost),
        "unit_contribution_margin": unit_price - unit_variable_cost,
    }
