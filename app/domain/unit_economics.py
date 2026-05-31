from __future__ import annotations

from decimal import Decimal


def money(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value))


def calculate_gross_margin(revenue: Decimal, variable_cost: Decimal) -> Decimal:
    return money(revenue) - money(variable_cost)


def calculate_gross_margin_percentage(revenue: Decimal, variable_cost: Decimal) -> Decimal:
    revenue = money(revenue)
    if revenue == 0:
        return Decimal("0")
    return calculate_gross_margin(revenue, variable_cost) / revenue


def calculate_operating_margin(
    revenue: Decimal,
    variable_cost: Decimal,
    allocated_fixed_cost: Decimal,
) -> Decimal:
    return money(revenue) - money(variable_cost) - money(allocated_fixed_cost)


def calculate_minimum_unit_price(unit_cost: Decimal, target_margin: Decimal) -> Decimal:
    unit_cost = money(unit_cost)
    target_margin = money(target_margin)
    if target_margin < 0 or target_margin >= 1:
        raise ValueError("target_margin must be between 0 and 1, exclusive of 1")
    return unit_cost / (Decimal("1") - target_margin)


def calculate_break_even_clients(fixed_costs: Decimal, average_margin_per_client: Decimal) -> int:
    fixed_costs = money(fixed_costs)
    average_margin_per_client = money(average_margin_per_client)
    if average_margin_per_client <= 0:
        raise ValueError("average_margin_per_client must be greater than zero")
    return int((fixed_costs / average_margin_per_client).to_integral_value(rounding="ROUND_CEILING"))


def calculate_break_even_usage(
    fixed_costs: Decimal,
    unit_price: Decimal,
    unit_variable_cost: Decimal,
) -> int:
    contribution_margin = money(unit_price) - money(unit_variable_cost)
    if contribution_margin <= 0:
        raise ValueError("unit_price must be greater than unit_variable_cost")
    return int((money(fixed_costs) / contribution_margin).to_integral_value(rounding="ROUND_CEILING"))
