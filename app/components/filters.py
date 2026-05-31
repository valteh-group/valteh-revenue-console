import dash_bootstrap_components as dbc
from dash import dcc

from app.utils.dates import available_months


def month_filter(component_id: str = "month-filter", value: str = "2026-05") -> dbc.Col:
    return dbc.Col(
        [
            dbc.Label("Month"),
            dcc.Dropdown(
                id=component_id,
                options=[{"label": month, "value": month} for month in available_months()],
                value=value,
                clearable=False,
            ),
        ],
        md=3,
    )


def scenario_filter(component_id: str = "scenario-filter") -> dbc.Col:
    scenarios = ["Base case", "Conservative case", "Growth case", "Stress case"]
    return dbc.Col(
        [
            dbc.Label("Scenario"),
            dcc.Dropdown(
                id=component_id,
                options=[{"label": scenario, "value": scenario} for scenario in scenarios],
                value="Base case",
                clearable=False,
            ),
        ],
        md=3,
    )
