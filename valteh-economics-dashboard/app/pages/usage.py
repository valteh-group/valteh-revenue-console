from dash import html

from app.components.tables import data_table
from app.data.repositories import SeedRepository


def layout():
    repo = SeedRepository()
    rows = [
        {
            "client_id": event.client_id,
            "service_code": event.service_code,
            "event_type": event.event_type,
            "quantity": float(event.quantity),
            "unit": event.unit,
            "timestamp": event.event_timestamp.strftime("%Y-%m-%d"),
            "source_system": event.source_system,
        }
        for event in repo.usage_events()
    ]
    return html.Div(
        [
            html.H1("Usage", className="h3"),
            html.P("Seeded operational usage events by service line.", className="text-muted"),
            data_table("usage-table", rows, 15),
        ]
    )
