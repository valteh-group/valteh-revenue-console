from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

from app.components.charts import bar_chart, line_chart
from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.domain.cost_engine import calculate_fixed_costs, is_cost_effective
from app.utils.currency import format_mxn


def layout():
    repo = SeedRepository()
    items = repo.cost_items()
    selected_month = repo.available_months()[-1]
    today = date.today()
    current_items = [item for item in items if is_cost_effective(item, today)]
    current_fixed = calculate_fixed_costs([item for item in items if item.cost_type == "fixed"], today.replace(day=1))
    rows = [
        {
            "cost_key": item.cost_key,
            "name": item.name,
            "provider": item.provider or "",
            "category": item.category,
            "service_line": item.service_line or "Shared",
            "cost_type": item.cost_type,
            "record_type": item.record_type,
            "quantity": f"{item.quantity:f}",
            "unit_cost": f"{float(item.unit_cost):,.4f}",
            "configured_amount": format_mxn(item.configured_amount),
            "unit": item.unit,
            "frequency": item.billing_frequency,
            "start_date": item.start_date.isoformat() if item.start_date else "",
            "end_date": item.end_date.isoformat() if item.end_date else "",
            "enabled": item.enabled,
            "notes": item.notes or "",
        }
        for item in items
    ]
    monthly_rows = [
        {
            "cost_key": cost.cost_key,
            "name": cost.name,
            "provider": cost.provider or "",
            "category": cost.category,
            "service_line": cost.service_line,
            "cost_type": cost.cost_type,
            "quantity": f"{cost.quantity:f}",
            "unit_cost": f"{float(cost.unit_cost):,.4f}",
            "unit": cost.unit,
            "amount": format_mxn(cost.amount),
            "start_date": cost.start_date.isoformat() if cost.start_date else "",
            "end_date": cost.end_date.isoformat() if cost.end_date else "",
        }
        for cost in repo.monthly_cost_amounts(selected_month)
    ]
    history = pd.DataFrame(repo.cost_history())
    return html.Div(
        [
            html.H1("Costs", className="h3"),
            html.P(
                "Effective-dated fixed costs, variable rates, one-time costs, and assumptions.",
                className="text-muted",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(dbc.CardBody([html.Small("Current actual versions"), html.H3(len(current_items))])),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([html.Small("Current monthly fixed cost"), html.H3(format_mxn(current_fixed))])
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Small("Scheduled future versions"),
                                    html.H3(sum(1 for item in items if item.start_date and item.start_date > today)),
                                ]
                            )
                        ),
                        md=4,
                    ),
                ],
                className="g-3 mb-3",
            ),
            dbc.Alert(
                [
                    html.Strong("To change a price without losing history: "),
                    "set the old row's end_date, then add a new row with the same cost_key and the new start_date. "
                    "Keep actual, budget, and estimate records separate with record_type.",
                ],
                color="info",
            ),
            html.H2(f"Realized Costs for {selected_month}", className="h5"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(figure=bar_chart(repo.cost_by_service(selected_month), "Costs by Service Line")),
                        md=4,
                    ),
                    dbc.Col(
                        dcc.Graph(figure=bar_chart(repo.cost_by_provider(selected_month), "Costs by Provider")),
                        md=4,
                    ),
                    dbc.Col(
                        dcc.Graph(figure=bar_chart(repo.cost_by_category(selected_month), "Costs by Category")),
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Card(
                dbc.CardBody(data_table("monthly-costs-table", monthly_rows, 10)),
                className="border-0 shadow-sm mb-4",
            ),
            html.H2("Cost History", className="h5"),
            dbc.Card(
                dbc.CardBody(dcc.Graph(figure=line_chart(history, "month", "total", "Total Cost History"))),
                className="border-0 shadow-sm mb-4",
            ),
            html.H2("Catalog Versions", className="h5"),
            dbc.Card(dbc.CardBody(data_table("costs-table", rows, 15)), className="border-0 shadow-sm"),
        ]
    )
