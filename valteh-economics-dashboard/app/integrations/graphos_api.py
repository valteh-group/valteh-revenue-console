from datetime import datetime


def fetch_graphos_usage() -> list[dict]:
    return [
        {
            "service_code": "graphos",
            "event_type": "graphos.query",
            "quantity": 300,
            "unit": "query",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "graphos_mock",
        }
    ]
