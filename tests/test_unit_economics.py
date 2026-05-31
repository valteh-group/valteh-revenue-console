from decimal import Decimal

import pytest

from app.domain.unit_economics import (
    calculate_break_even_clients,
    calculate_break_even_usage,
    calculate_gross_margin,
    calculate_gross_margin_percentage,
    calculate_minimum_unit_price,
    calculate_operating_margin,
)


def test_margin_calculations() -> None:
    assert calculate_gross_margin(Decimal("100"), Decimal("35")) == Decimal("65")
    assert calculate_operating_margin(Decimal("100"), Decimal("35"), Decimal("20")) == Decimal("45")
    assert calculate_gross_margin_percentage(Decimal("100"), Decimal("35")) == Decimal("0.65")


def test_minimum_unit_price() -> None:
    assert calculate_minimum_unit_price(Decimal("40"), Decimal("0.60")) == Decimal("100")


def test_break_even_calculations() -> None:
    assert calculate_break_even_clients(Decimal("1000"), Decimal("250")) == 4
    assert calculate_break_even_usage(Decimal("1000"), Decimal("30"), Decimal("10")) == 50


def test_invalid_break_even_inputs() -> None:
    with pytest.raises(ValueError):
        calculate_break_even_clients(Decimal("1000"), Decimal("0"))
    with pytest.raises(ValueError):
        calculate_break_even_usage(Decimal("1000"), Decimal("10"), Decimal("10"))
