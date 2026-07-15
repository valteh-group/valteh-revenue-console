"""Client for source-system operational-event export endpoints.

Implements the pull side of the shared contract: each source system exposes
``GET /api/operational-events`` (cursor-paginated). See
docs/shared-operational-event-contract.md section 9.
"""

from __future__ import annotations

from typing import Protocol

import httpx

from app.config import SourceConfig
from app.domain.operational_events import OperationalEventPage

EXPORT_PATH = "/api/operational-events"


class OperationalEventSource(Protocol):
    """Anything that can return one page of operational events.

    Defined as a Protocol so the ingestion service can be driven by a fake
    source in tests without any network access.
    """

    source_system: str

    def fetch_page(self, cursor: str | None, limit: int) -> OperationalEventPage: ...


class HttpOperationalEventSource:
    """Pulls operational events from a source system over HTTP."""

    def __init__(self, config: SourceConfig, *, client: httpx.Client | None = None, timeout: float = 30.0) -> None:
        self.source_system = config.source_system
        self._base_url = config.base_url.rstrip("/")
        self._token = config.token
        self._client = client or httpx.Client(timeout=timeout)

    def fetch_page(self, cursor: str | None, limit: int) -> OperationalEventPage:
        params: dict[str, str | int] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        response = self._client.get(
            f"{self._base_url}{EXPORT_PATH}",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return OperationalEventPage.model_validate(response.json())

    def close(self) -> None:
        self._client.close()
