from datetime import datetime


def fetch_blockchain_usage() -> list[dict]:
    return [
        {
            "service_code": "blockchain",
            "event_type": "blockchain.folio_mint",
            "quantity": 20,
            "unit": "folio",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "blockchain_mock",
        }
    ]
