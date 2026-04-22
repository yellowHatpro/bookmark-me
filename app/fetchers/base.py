from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class FetcherError(Exception):
    """Generic fetcher failure worth reporting to the user."""


class AuthError(FetcherError):
    """Raised when the platform rejects the session (cookies expired / bad CSRF)."""


@dataclass
class FetchedItem:
    platform: str
    external_id: str
    url: str
    title: str | None = None
    text: str | None = None
    author_handle: str | None = None
    author_name: str | None = None
    media: list[dict[str, Any]] = field(default_factory=list)
    saved_at: datetime | None = None


@dataclass
class FetchResult:
    items: list[FetchedItem]
    hit_known: bool = False  # True if pagination stopped because we saw an already-stored id


class Fetcher(ABC):
    platform: str

    @abstractmethod
    async def iter_items(
        self,
        cookies: dict[str, str],
        extra: dict[str, Any],
        known_ids: set[str],
        hard_cap: int,
    ) -> AsyncIterator[FetchedItem]:
        """Yield items newest-first, stopping once a known external_id is seen or hard_cap hit."""
        raise NotImplementedError
        yield  # pragma: no cover
