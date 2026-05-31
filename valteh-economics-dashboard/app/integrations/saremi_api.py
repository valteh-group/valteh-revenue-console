from datetime import datetime


def fetch_saremi_usage() -> list[dict]:
    return [
        {
            "service_code": "saremi",
            "event_type": "saremi.document_validation",
            "quantity": 120,
            "unit": "document",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "saremi_mock",
        }
    ]
