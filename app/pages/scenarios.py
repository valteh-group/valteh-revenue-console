from decimal import Decimal

import dash_bootstrap_components as dbc
from dash import Input, Output, html

from app.components.filters import scenario_filter
from app.components.kpi_card import kpi_card
from app.domain.unit_economics import calculate_break_even_clients
from app.utils.currency import format_mxn, format_percent

SCENARIOS = {
    "Base case": {
        "clients": 3,
        "documents": 597,
        "validations": 85,
        "graph_queries": 115,
        "transactions": 43,
        "folios": 0,
        "fixed_costs": 570,
    },
    "Conservative case": {
        "clients": 1,
        "documents": 168,
        "validations": 24,
        "graph_queries": 30,
        "transactions": 12,
        "folios": 0,
        "fixed_costs": 570,
    },
    "Growth case": {
        "clients": 10,
        "documents": 700,
        "validations": 100,
        "graph_queries": 140,
        "transactions": 50,
        "folios": 0,
        "fixed_costs": 1500,
    },
    "Stress case": {
        "clients": 3,
        "documents": 1200,
        "validations": 170,
        "graph_queries": 300,
        "transactions": 90,
        "folios": 0,
        "fixed_costs": 570,
    },
}


def layout():
    return html.Div(
        [
            html.H1("Scenarios", className="h3"),
            html.P("Base, conservative, growth, and stress case projections.", className="text-muted"),
            dbc.Row([scenario_filter()], className="mb-4"),
            html.Div(id="scenario-results", children=_scenario_content("Base case")),
        ]
    )


def register_callbacks(app) -> None:
    @app.callback(Output("scenario-results", "children"), Input("scenario-filter", "value"))
    def update_scenario(scenario_name: str):
        return _scenario_content(scenario_name)


def _scenario_content(scenario_name: str):
    scenario = SCENARIOS[scenario_name]
    revenue = Decimal(scenario["clients"]) * Decimal("4000")
    usage_revenue = Decimal(scenario["clients"]) * (
        Decimal(scenario["documents"]) * Decimal("6")
        + Decimal(scenario["validations"]) * Decimal("2")
        + Decimal(scenario["graph_queries"]) * Decimal("1")
        + Decimal(scenario["transactions"]) * Decimal("0.5")
        + Decimal(scenario["folios"]) * Decimal("0")
    )
    total_revenue = revenue + usage_revenue
    variable_cost = Decimal(scenario["clients"]) * (
        Decimal(scenario["documents"]) * Decimal("1.00")
        + Decimal(scenario["validations"]) * Decimal("0.10")
        + Decimal(scenario["graph_queries"]) * Decimal("0.02")
        + Decimal(scenario["transactions"]) * Decimal("0.01")
    )
    fixed_cost = Decimal(scenario["fixed_costs"])
    margin = total_revenue - variable_cost - fixed_cost
    margin_pct = margin / total_revenue if total_revenue else Decimal("0")
    break_even_clients = calculate_break_even_clients(
        fixed_cost, (total_revenue - variable_cost) / Decimal(scenario["clients"])
    )

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        kpi_card(
                            "Projected Revenue",
                            format_mxn(total_revenue),
                            tooltip="Scenario revenue: monthly fixed fees plus estimated usage-based fees.",
                            card_id="scenario-projected-revenue",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Projected Variable Cost",
                            format_mxn(variable_cost),
                            color="warning",
                            tooltip="Scenario usage costs based on document, ID validation, graph, "
                            "and audit-anchor volumes.",
                            card_id="scenario-variable-cost",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Projected Operating Margin",
                            format_mxn(margin),
                            color="success" if margin > 0 else "danger",
                            tooltip="Projected profit after variable costs and fixed costs.",
                            card_id="scenario-operating-margin",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Margin Percentage",
                            format_percent(margin_pct),
                            tooltip="Projected operating margin divided by projected revenue.",
                            card_id="scenario-margin-percentage",
                        ),
                        md=3,
                    ),
                ],
                className="g-3 mb-3",
            ),
            dbc.Alert(
                f"Break-even number of clients under the {scenario_name.lower()}: {break_even_clients}",
                color="primary",
            ),
        ]
    )
