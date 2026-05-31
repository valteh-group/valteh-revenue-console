from decimal import Decimal

import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

from app.components.charts import bar_chart, pie_chart
from app.components.filters import month_filter
from app.components.kpi_card import kpi_card
from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.domain.unit_economics import calculate_break_even_usage
from app.utils.currency import format_mxn, format_percent


def layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Executive Dashboard", className="h3"),
                    html.P("Monthly economics overview", className="text-muted"),
                ]
            ),
            dbc.Row([month_filter("executive-month-filter", "2026-06")], className="mb-3"),
            html.Div(id="executive-dashboard-content", children=_dashboard_content("2026-06")),
        ]
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("executive-dashboard-content", "children"),
        Input("executive-month-filter", "value"),
    )
    def update_dashboard(month: str):
        return _dashboard_content(month)


def _dashboard_content(month: str):
    repo = SeedRepository()
    summary = repo.monthly_summary(month)
    revenue_by_service = repo.revenue_by_service(month)
    cost_by_service = repo.cost_by_service(month)
    variable_cost = summary["variable_cost"]
    revenue = summary["revenue"]
    gross_margin_pct = (summary["gross_margin"] / revenue) if revenue else Decimal("0")
    operating_margin_pct = (summary["operating_margin"] / revenue) if revenue else Decimal("0")
    break_even_usage = calculate_break_even_usage(summary["fixed_cost"], Decimal("6"), Decimal("1.10"))
    client_rows = _client_rows(repo, month)
    lowest_margin_rows = sorted(client_rows, key=lambda row: row["gross_margin_percentage"])[:5]

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        kpi_card(
                            "Monthly Revenue",
                            format_mxn(revenue),
                            tooltip="Total subscription and billable usage revenue recognized in the selected month.",
                            card_id="executive-monthly-revenue",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Fixed Costs",
                            format_mxn(summary["fixed_cost"]),
                            color="secondary",
                            tooltip="Monthly active fixed costs, independent of usage volume.",
                            card_id="executive-fixed-costs",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Variable Costs",
                            format_mxn(variable_cost),
                            color="warning",
                            tooltip="Usage-driven costs: sum of each usage event quantity multiplied by its unit cost.",
                            card_id="executive-variable-costs",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Gross Margin",
                            format_percent(gross_margin_pct),
                            color="success",
                            tooltip="Gross margin percentage: (revenue minus variable costs) divided by revenue.",
                            card_id="executive-gross-margin",
                        ),
                        md=3,
                    ),
                ],
                className="g-3 mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        kpi_card(
                            "Operating Margin",
                            format_percent(operating_margin_pct),
                            color="success" if operating_margin_pct > 0 else "danger",
                            tooltip="Operating margin percentage: revenue minus variable and fixed costs, "
                            "divided by revenue.",
                            card_id="executive-operating-margin",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Burn Rate",
                            format_mxn(summary["burn_rate"]),
                            color="danger",
                            tooltip="Cash consumed in the month when operating margin is negative; zero if profitable.",
                            card_id="executive-burn-rate",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Break-even Usage",
                            f"{break_even_usage:,} docs",
                            "At $6 price and $1.10 unit cost",
                            tooltip="Documents needed to cover fixed costs: fixed costs divided by unit "
                            "contribution margin.",
                            card_id="executive-break-even-usage",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "Active Clients",
                            str(len(repo.active_clients(month))),
                            tooltip="Clients with an active subscription during the selected month.",
                            card_id="executive-active-clients",
                        ),
                        md=3,
                    ),
                ],
                className="g-3 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=pie_chart(revenue_by_service, "Revenue by Service Line")), md=4),
                    dbc.Col(dcc.Graph(figure=bar_chart(cost_by_service, "Cost by Service Line")), md=4),
                    dbc.Col(
                        dcc.Graph(
                            figure=bar_chart(
                                _margin_by_service(revenue_by_service, cost_by_service),
                                "Margin by Service Line",
                            )
                        ),
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Top Clients by Revenue", className="h5"),
                            data_table("top-clients", _display_rows(client_rows[:5]), 5),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H2("Lowest-margin Clients", className="h5"),
                            data_table("low-margin-clients", _display_rows(lowest_margin_rows), 5),
                        ],
                        md=6,
                    ),
                ]
            ),
        ]
    )


def _client_rows(repo: SeedRepository, month: str) -> list[dict]:
    rows = []
    for client in repo.active_clients(month):
        profitability = repo.client_profitability(client.id, month)
        rows.append(
            {
                "client": client.name,
                "revenue": format_mxn(profitability.revenue),
                "revenue_value": float(profitability.revenue),
                "variable_cost": format_mxn(profitability.variable_cost),
                "gross_margin": format_mxn(profitability.gross_margin),
                "gross_margin_percentage": float(profitability.gross_margin_percentage),
            }
        )
    return sorted(rows, key=lambda row: row["revenue_value"], reverse=True)


def _display_rows(rows: list[dict]) -> list[dict]:
    return [{key: value for key, value in row.items() if key != "revenue_value"} for row in rows]


def _margin_by_service(revenue: dict[str, Decimal], costs: dict[str, Decimal]) -> dict[str, Decimal]:
    return {service: amount - costs.get(service, Decimal("0")) for service, amount in revenue.items()}
