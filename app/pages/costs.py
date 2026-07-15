from datetime import date

import dash_bootstrap_components as dbc
from dash import html

from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.domain.cost_engine import calculate_fixed_costs, is_cost_effective
from app.utils.currency import format_mxn


def layout():
    repo = SeedRepository()
    items = repo.cost_items()
    today = date.today()
    current_items = [item for item in items if is_cost_effective(item, today)]
    current_fixed = calculate_fixed_costs(
        [item for item in items if item.cost_type == "fixed"], today.replace(day=1)
    )
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
            "charge_day": item.charge_day or "",
            "start_date": item.start_date.isoformat() if item.start_date else "",
            "end_date": item.end_date.isoformat() if item.end_date else "",
            "enabled": item.enabled,
            "notes": item.notes or "",
        }
        for item in items
    ]
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
                            dbc.CardBody(
                                [html.Small("Current monthly fixed cost"), html.H3(format_mxn(current_fixed))]
                            )
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
            dbc.Card(dbc.CardBody(data_table("costs-table", rows, 15)), className="border-0 shadow-sm"),
        ]
    )
