"""Rebuild the Postgres bookmark index from the markdown vault.

This is the "DB died, restore everything from SSoT" path. Accounts still need
to exist (pasted cookies live encrypted in the DB and are intentionally *not*
in the vault) -- so the flow is:

    1. Re-add each account via the Settings UI (platform + label + cookies).
    2. `uv run python scripts/restore_from_vault.py`
    3. The script matches vault rows to accounts by (platform, account_label),
       falling back to the single account of that platform if unambiguous.

Bookmarks are upserted by (platform, external_id) -- safe to re-run.

Usage:
    uv run python scripts/restore_from_vault.py           # real run
    uv run python scripts/restore_from_vault.py --dry-run # report what would change
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import vault  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import Account, Bookmark  # noqa: E402


log = logging.getLogger("restore_from_vault")


async def _resolve_account_id(
    session: AsyncSession,
    platform: str,
    label: str | None,
    cache: dict[tuple[str, str | None], int | None],
) -> int | None:
    key = (platform, label)
    if key in cache:
        return cache[key]

    accounts = (
        await session.execute(select(Account).where(Account.platform == platform))
    ).scalars().all()

    if not accounts:
        cache[key] = None
        return None

    if label:
        for a in accounts:
            if a.label == label:
                cache[key] = a.id
                return a.id

    # No explicit label match: only auto-pick if unambiguous.
    if len(accounts) == 1:
        cache[key] = accounts[0].id
        return accounts[0].id

    cache[key] = None
    return None


async def restore(*, dry_run: bool) -> tuple[int, int, int]:
    """Returns (inserted_or_updated, skipped_no_account, errors)."""
    inserted = skipped = errors = 0
    cache: dict[tuple[str, str | None], int | None] = {}

    async with SessionLocal() as session:
        for path in vault.iter_vault():
            try:
                record = vault.parse_bookmark_md(path)
            except Exception as exc:  # noqa: BLE001
                log.warning("Skipping %s: parse error: %s", path, exc)
                errors += 1
                continue

            account_id = await _resolve_account_id(
                session, record.platform, record.account_label, cache
            )
            if account_id is None:
                log.warning(
                    "Skipping %s: no matching %s account (label=%r). "
                    "Add the account in Settings first.",
                    path,
                    record.platform,
                    record.account_label,
                )
                skipped += 1
                continue

            stmt = (
                pg_insert(Bookmark)
                .values(
                    account_id=account_id,
                    platform=record.platform,
                    external_id=record.external_id,
                    url=record.url,
                    title=record.title,
                    text=record.text,
                    author_handle=record.author_handle,
                    author_name=record.author_name,
                    media_json=record.media,
                    saved_at=record.saved_at,
                    archived=record.archived,
                )
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["platform", "external_id"],
                set_={
                    "url": stmt.excluded.url,
                    "title": stmt.excluded.title,
                    "text": stmt.excluded.text,
                    "author_handle": stmt.excluded.author_handle,
                    "author_name": stmt.excluded.author_name,
                    "media_json": stmt.excluded.media_json,
                    "saved_at": stmt.excluded.saved_at,
                    "archived": stmt.excluded.archived,
                },
            )

            if dry_run:
                inserted += 1
                continue

            await session.execute(stmt)
            inserted += 1

        if not dry_run:
            await session.commit()

    return inserted, skipped, errors


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report actions without writing to DB.")
    args = parser.parse_args()

    inserted, skipped, errors = asyncio.run(restore(dry_run=args.dry_run))
    verb = "would upsert" if args.dry_run else "upserted"
    log.info(
        "%s %d bookmarks; skipped %d (no matching account); %d parse errors.",
        verb,
        inserted,
        skipped,
        errors,
    )


if __name__ == "__main__":
    main()
