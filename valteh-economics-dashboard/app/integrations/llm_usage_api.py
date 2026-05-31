from datetime import datetime


def fetch_llm_token_usage() -> list[dict]:
    return [
        {
            "event_type": "saremi.llm_tokens_input",
            "quantity": 250000,
            "unit": "token",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "llm_mock",
        }
    ]
