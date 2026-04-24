from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Platform = Literal["x", "reddit"]


class AccountCreate(BaseModel):
    platform: Platform
    label: str = Field(min_length=1, max_length=128)
    raw_cookies: str = Field(description="Raw `Cookie:` header copied from browser DevTools")
    username: str | None = Field(
        default=None,
        description="Required for Reddit (used to fetch /user/<name>/saved.json)",
    )


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    label: str
    status: str
    last_error: str | None
    last_synced_at: datetime | None
    created_at: datetime
    extra_json: dict[str, Any]


class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    platform: str
    external_id: str
    url: str
    title: str | None
    text: str | None
    author_handle: str | None
    author_name: str | None
    media_json: list[dict[str, Any]]
    saved_at: datetime | None
    fetched_at: datetime
    archived: bool


class BookmarkListOut(BaseModel):
    items: list[BookmarkOut]
    total: int
    limit: int
    offset: int


class SyncRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    started_at: datetime
    finished_at: datetime | None
    ok: bool
    new_count: int
    error: str | None


class ArchiveUpdate(BaseModel):
    archived: bool


VaultDirSource = Literal["env", "user_config", "default"]


class VaultSettings(BaseModel):
    path: str
    source: VaultDirSource
    env_override_active: bool
    exists: bool
    file_count: int


class VaultSettingsUpdate(BaseModel):
    path: str = Field(
        min_length=1,
        description="Absolute path, or a `~`-prefixed path. Tilde is expanded server-side.",
    )
    move: bool = Field(
        default=False,
        description=(
            "Move existing vault contents to the new path. Requires the "
            "destination to be empty or nonexistent."
        ),
    )
