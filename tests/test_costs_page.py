from decimal import Decimal

from app.pages.costs import _month_options, _summarize_cost_rows, _year_cost_chart


def _cost_row(month: str, fixed: str, variable: str, one_time: str = "0") -> dict:
    fixed_amount = Decimal(fixed)
    variable_amount = Decimal(variable)
    one_time_amount = Decimal(one_time)
    return {
        "month": month,
        "fixed": fixed_amount,
        "variable": variable_amount,
        "one_time": one_time_amount,
        "total": fixed_amount + variable_amount + one_time_amount,
    }


def test_cost_summary_reconciles_fixed_variable_and_one_time_costs() -> None:
    split = _summarize_cost_rows(
        [
            _cost_row("2026-01", "100", "20", "50"),
            _cost_row("2026-02", "120", "30"),
        ]
    )

    assert split == {
        "fixed": Decimal("270"),
        "variable": Decimal("50"),
        "total": Decimal("320"),
    }


def test_year_chart_stacks_fixed_and_variable_monthly_costs() -> None:
    figure = _year_cost_chart(
        [
            _cost_row("2026-01", "100", "20", "50"),
            _cost_row("2026-02", "120", "30"),
        ],
        2026,
    )

    traces = {trace.name: list(trace.y) for trace in figure.data}
    assert traces == {
        "Fixed + one-time": [150.0, 120.0],
        "Variable": [20.0, 30.0],
    }
    assert figure.layout.xaxis.type == "category"
    assert figure.layout.xaxis.tickformat == "%Y-%m"
    assert all("%{fullData.name}" in trace.hovertemplate for trace in figure.data)


def test_month_options_are_limited_to_selected_available_year() -> None:
    options = _month_options(["2025-12", "2026-01", "2026-02"], "2026")

    assert options == [
        {"label": "January", "value": "2026-01"},
        {"label": "February", "value": "2026-02"},
    ]
