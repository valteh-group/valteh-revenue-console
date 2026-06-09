"""Entry point to synchronize operational events from all configured sources.

Run with:

    python -m app.integrations.sync_runner

Reads source configuration from the environment (see app/config.py and
.env.example) and ingests new events into the local database.
"""

from __future__ import annotations

from app.config import get_settings
from app.data.database import SessionLocal, init_db
from app.integrations.ingestion import SyncResult, sync_source
from app.integrations.operational_events_client import HttpOperationalEventSource


def run_sync() -> list[SyncResult]:
    """Synchronize every configured source system. Returns one result each."""

    settings = get_settings()
    init_db()

    results: list[SyncResult] = []
    for source_config in settings.event_sources():
        source = HttpOperationalEventSource(source_config)
        session = SessionLocal()
        try:
            results.append(sync_source(session, source, page_size=source_config.page_size))
        finally:
            session.close()
            source.close()
    return results


def main() -> None:
    results = run_sync()
    if not results:
        print("No operational-event sources configured. Set *_EVENTS_URL in .env.")
        return
    for result in results:
        if result.error:
            print(f"[{result.source_system}] ERROR: {result.error}")
        print(
            f"[{result.source_system}] imported={result.imported} "
            f"skipped={result.skipped} pages={result.pages} "
            f"last_occurred_at={result.last_occurred_at}"
        )


if __name__ == "__main__":
    main()
