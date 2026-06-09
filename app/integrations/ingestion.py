"""Idempotent ingestion of operational events from source systems.

Pulls cursor-paginated pages from each source, stores raw facts in
``imported_operational_events`` deduplicated by ``(source_system,
source_event_id)``, and tracks sync progress in ``event_import_cursors``.

This is Phase 1 (ingestion foundation): it does not classify, price, or
normalize events. It only lands raw facts safely and idempotently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.schemas import EventImportCursorORM, ImportedOperationalEventORM
from app.domain.operational_events import OperationalEvent
from app.integrations.operational_events_client import OperationalEventSource

# Safety bound so a misbehaving source (e.g. a cursor that never advances)
# cannot loop forever within a single sync run.
MAX_PAGES_PER_SYNC = 1000


@dataclass
class SyncResult:
    """Outcome of synchronizing one source system."""

    source_system: str
    imported: int = 0
    skipped: int = 0
    pages: int = 0
    last_occurred_at: datetime | None = None
    error: str | None = None
    errors: list[str] = field(default_factory=list)


def _to_orm(event: OperationalEvent) -> ImportedOperationalEventORM:
    return ImportedOperationalEventORM(
        source_system=event.source_system,
        source_event_id=event.id,
        event_type=event.event_type,
        event_category=event.event_category,
        occurred_at=event.occurred_at,
        recorded_at=event.recorded_at,
        received_at=datetime.utcnow(),
        correlation_id=event.correlation_id,
        causation_id=event.causation_id,
        external_reference_id=event.external_reference_id,
        source_client_ref=event.client_reference,
        entity_id=event.entity_id,
        document_id=event.document_id,
        document_hash=event.document_hash,
        property_id=event.property_id,
        profile_id=event.profile_id,
        transaction_id=event.transaction_id,
        status=event.status,
        quantity=event.quantity,
        unit=event.unit,
        raw_payload_json=event.model_dump_json(),
        import_status="imported",
    )


def _existing_ids(session: Session, source_system: str, source_event_ids: list[str]) -> set[str]:
    if not source_event_ids:
        return set()
    rows = session.execute(
        select(ImportedOperationalEventORM.source_event_id).where(
            ImportedOperationalEventORM.source_system == source_system,
            ImportedOperationalEventORM.source_event_id.in_(source_event_ids),
        )
    ).scalars()
    return set(rows)


def _get_or_create_cursor(session: Session, source_system: str) -> EventImportCursorORM:
    cursor = session.get(EventImportCursorORM, source_system)
    if cursor is None:
        cursor = EventImportCursorORM(source_system=source_system)
        session.add(cursor)
    return cursor


def sync_source(session: Session, source: OperationalEventSource, page_size: int = 200) -> SyncResult:
    """Pull all available pages from one source and persist new events.

    Resumes from the stored cursor, deduplicates by ``(source_system,
    source_event_id)``, and advances the cursor only after a page is persisted,
    so a crash mid-run is safe to retry.
    """

    result = SyncResult(source_system=source.source_system)
    cursor_row = _get_or_create_cursor(session, source.source_system)
    cursor = cursor_row.cursor

    try:
        for _ in range(MAX_PAGES_PER_SYNC):
            page = source.fetch_page(cursor, page_size)
            result.pages += 1

            events = page.data
            incoming_ids = [event.id for event in events]
            existing = _existing_ids(session, source.source_system, incoming_ids)

            # Guard against duplicates within the same page as well.
            seen_in_page: set[str] = set()
            for event in events:
                if event.id in existing or event.id in seen_in_page:
                    result.skipped += 1
                    continue
                seen_in_page.add(event.id)
                session.add(_to_orm(event))
                result.imported += 1
                if result.last_occurred_at is None or event.occurred_at > result.last_occurred_at:
                    result.last_occurred_at = event.occurred_at

            # Persist the page and the advanced cursor together.
            cursor = page.pagination.next_cursor
            cursor_row.cursor = cursor
            if result.last_occurred_at is not None:
                cursor_row.last_occurred_at = result.last_occurred_at
            cursor_row.status = "ok"
            cursor_row.error_message = None
            session.commit()

            if not page.pagination.has_more or cursor is None:
                break
        else:
            # Loop exhausted MAX_PAGES_PER_SYNC without finishing.
            result.error = f"Stopped after {MAX_PAGES_PER_SYNC} pages; cursor may not be advancing."
            cursor_row.status = "error"
            cursor_row.error_message = result.error
            session.commit()

        cursor_row.last_successful_sync_at = datetime.utcnow()
        session.commit()
    except Exception as exc:  # noqa: BLE001 - record any sync failure on the cursor.
        session.rollback()
        cursor_row = _get_or_create_cursor(session, source.source_system)
        cursor_row.status = "error"
        cursor_row.error_message = str(exc)
        session.commit()
        result.error = str(exc)

    return result
