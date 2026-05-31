import dash_bootstrap_components as dbc
from dash import html

from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.utils.currency import format_mxn


def layout():
    repo = SeedRepository()
    rows = [
        {
            "name": item.name,
            "category": item.category,
            "service_line": item.service_line or "Shared",
            "cost_type": item.cost_type,
            "monthly_amount": format_mxn(item.monthly_amount),
            "one_time_amount": format_mxn(item.one_time_amount),
            "start_date": item.start_date.isoformat() if item.start_date else "",
            "unit_cost": f"{float(item.unit_cost):,.4f}",
            "unit": item.unit or "",
            "active": item.active,
        }
        for item in repo.cost_items()
    ]
    return html.Div(
        [
            html.H1("Costs", className="h3"),
            html.P("Fixed costs, variable rates, monthly costs, and assumptions.", className="text-muted"),
            dbc.Alert(
                "Cost editing will be added on top of this repository layer; current values are seeded from CSV.",
                color="info",
            ),
            dbc.Card(dbc.CardBody(data_table("costs-table", rows, 15)), className="border-0 shadow-sm"),
        ]
    )
