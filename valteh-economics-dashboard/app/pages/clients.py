from decimal import Decimal

import dash_bootstrap_components as dbc
from dash import html

from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.utils.currency import format_mxn, format_percent


def layout():
    repo = SeedRepository()
    month = "2026-06"
    rows = []
    for client in repo.clients():
        usage = repo.usage_for_client_month(client.id, month)
        profitability = repo.client_profitability(client.id, month)
        plan = repo.active_plan_for_client(client.id)
        margin_pct = profitability.gross_margin_percentage
        alert = (
            "Low margin"
            if margin_pct < Decimal("0.45")
            else "High usage" if sum(event.quantity for event in usage) > 6000 else "OK"
        )
        rows.append(
            {
                "client_name": client.name,
                "status": client.status,
                "active_services": ", ".join(sorted({event.service_code for event in usage})),
                "pricing_plan": plan.name,
                "monthly_revenue": format_mxn(profitability.revenue),
                "monthly_usage": f"{sum(event.quantity for event in usage):,.0f}",
                "monthly_variable_cost": format_mxn(profitability.variable_cost),
                "gross_margin": format_mxn(profitability.gross_margin),
                "gross_margin_percentage": format_percent(margin_pct),
                "alerts": alert,
            }
        )
    return html.Div(
        [
            html.H1("Clients / Notaries", className="h3"),
            html.P("Pilot and early-access client economics, usage, and margin alerts.", className="text-muted"),
            dbc.Card(dbc.CardBody(data_table("clients-table", rows, 10)), className="border-0 shadow-sm"),
        ]
    )
