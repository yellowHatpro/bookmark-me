"""On-disk markdown vault: the single source of truth for bookmarks.

Layout:
    vault/
      x/<external_id>.md
      reddit/<external_id>.md

Each file is YAML-frontmatter + CommonMark. Everything above the `## Notes`
heading is sync-owned and rewritten on every sync; everything below it is
user-owned and never touched. A deterministic emitter keeps diffs clean so the
vault can live in Syncthing/git/Obsidian without constant churn.

Read/write split intentionally stays on the sync path: writes happen in the
running event loop but target the local filesystem (no I/O contention with the
DB), so we use plain blocking I/O for simplicity.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.config import get_settings
from app.fetchers.base import FetchedItem

log = logging.getLogger(__name__)

NOTES_HEADING = "## Notes"
_USER_BLOCK_SEPARATOR = (
    f"\n{NOTES_HEADING}\n"
    "<!-- everything below this line is user-owned; sync never overwrites it -->\n"
)

# Filenames derived from external_ids are already safe in practice (tweet IDs
# are digits; reddit fullnames are `t<kind>_<base36>`). We still sanitise as a
# belt-and-braces measure in case a platform ever emits something weird.
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


@dataclass
class VaultRecord:
    """What we get back when we parse a vault file. Mirrors the Bookmark shape."""

    platform: str
    external_id: str
    url: str
    title: str | None
    text: str | None
    author_handle: str | None
    author_name: str | None
    media: list[dict[str, Any]]
    saved_at: datetime | None
    archived: bool
    account_label: str | None  # for matching back to an Account on restore
    notes: str | None           # user-owned block (below `## Notes`)


def vault_root() -> Path:
    """Resolve the configured vault dir, creating it if missing."""
    root = get_settings().vault_dir
    root.mkdir(parents=True, exist_ok=True)
    return root


def bookmark_path(platform: str, external_id: str) -> Path:
    safe = _SAFE_NAME.sub("_", external_id)
    return vault_root() / platform / f"{safe}.md"


# --------------------------------------------------------------------------
# Write path
# --------------------------------------------------------------------------


def write_bookmark(
    *,
    platform: str,
    external_id: str,
    url: str,
    title: str | None,
    text: str | None,
    author_handle: str | None,
    author_name: str | None,
    media: list[dict[str, Any]],
    saved_at: datetime | None,
    fetched_at: datetime | None = None,
    archived: bool = False,
    account_label: str | None = None,
) -> Path:
    """Render one bookmark to `{vault}/{platform}/{external_id}.md`.

    Idempotent. Preserves anything below the `## Notes` heading in an existing
    file so user notes survive re-syncs. Safe-write via tmp + os.replace so a
    crash mid-write can't produce a half-file.
    """
    path = bookmark_path(platform, external_id)
    preserved_notes = _read_user_notes(path)

    frontmatter: dict[str, Any] = {
        "platform": platform,
        "external_id": external_id,
        "url": url,
        "title": title,
        "author_handle": author_handle,
        "author_name": author_name,
        "saved_at": _iso(saved_at),
        "fetched_at": _iso(fetched_at) if fetched_at else _iso(_utcnow()),
        "archived": archived,
        "media": media or [],
        "account_label": account_label,
    }

    body_parts: list[str] = ["---", _dump_yaml(frontmatter).rstrip(), "---", ""]
    if title:
        body_parts.append(f"# {title}\n")
    if text:
        body_parts.append(text.rstrip() + "\n")

    body_parts.append(_USER_BLOCK_SEPARATOR.rstrip() + "\n")
    if preserved_notes:
        body_parts.append(preserved_notes.rstrip() + "\n")

    _safe_write(path, "\n".join(body_parts).rstrip() + "\n")
    return path


def write_from_item(item: FetchedItem, *, account_label: str | None) -> Path:
    """Convenience wrapper for the sync path, which has a FetchedItem in hand."""
    return write_bookmark(
        platform=item.platform,
        external_id=item.external_id,
        url=item.url,
        title=item.title,
        text=item.text,
        author_handle=item.author_handle,
        author_name=item.author_name,
        media=item.media,
        saved_at=item.saved_at,
        account_label=account_label,
    )


# --------------------------------------------------------------------------
# Read path
# --------------------------------------------------------------------------


def iter_vault() -> list[Path]:
    """All bookmark files in the vault, sorted for deterministic restore order."""
    root = vault_root()
    return sorted(p for p in root.rglob("*.md") if not p.name.startswith("_"))


def parse_bookmark_md(path: Path) -> VaultRecord:
    raw = path.read_text(encoding="utf-8")
    frontmatter, rest = _split_frontmatter(raw)
    body, notes = _split_notes(rest)

    text = _strip_title_heading(body, frontmatter.get("title")).strip() or None

    return VaultRecord(
        platform=str(frontmatter["platform"]),
        external_id=str(frontmatter["external_id"]),
        url=str(frontmatter.get("url") or ""),
        title=_nullable_str(frontmatter.get("title")),
        text=text,
        author_handle=_nullable_str(frontmatter.get("author_handle")),
        author_name=_nullable_str(frontmatter.get("author_name")),
        media=list(frontmatter.get("media") or []),
        saved_at=_parse_iso(frontmatter.get("saved_at")),
        archived=bool(frontmatter.get("archived", False)),
        account_label=_nullable_str(frontmatter.get("account_label")),
        notes=notes or None,
    )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _dump_yaml(data: dict[str, Any]) -> str:
    # sort_keys=False preserves the insertion order we chose in write_bookmark,
    # so diffs don't churn based on pyyaml's alphabetical default.
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10_000)


def _read_user_notes(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    _body, notes = _split_notes(_split_frontmatter(text)[1])
    return notes


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)", re.DOTALL)


def _split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    parsed = yaml.safe_load(m.group(1)) or {}
    if not isinstance(parsed, dict):
        return {}, m.group(2)
    return parsed, m.group(2)


_NOTES_RE = re.compile(r"^## Notes\b.*$", re.MULTILINE)


def _split_notes(rest: str) -> tuple[str, str | None]:
    """Split the post-frontmatter body into (sync_body, user_notes)."""
    m = _NOTES_RE.search(rest)
    if not m:
        return rest, None
    body = rest[: m.start()]
    after = rest[m.end():]
    # Drop the HTML marker comment on the line right after the heading, if any.
    after = re.sub(r"\A\s*<!--.*?-->\s*\n?", "", after, count=1, flags=re.DOTALL)
    return body, after.strip() or None


def _strip_title_heading(body: str, title: str | None) -> str:
    """If the sync-owned body starts with `# <title>`, drop it so we don't double-store."""
    if not title:
        return body
    pattern = re.compile(r"\A\s*#\s+" + re.escape(title) + r"\s*\n?", re.MULTILINE)
    return pattern.sub("", body, count=1)


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _nullable_str(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value)
    return s or None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
