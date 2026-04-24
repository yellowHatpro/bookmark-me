"""Re-emit the entire vault from the current DB.

Useful after:
  * Changing the vault file format (new frontmatter field, cleaner layout).
  * A partial vault (e.g. mounted the wrong folder for a while).

Safe: user notes under `## Notes` in existing files are preserved by
vault.write_bookmark.

Usage:
    uv run python scripts/rebuild_vault.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import vault  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import Account, Bookmark  # noqa: E402


log = logging.getLogger("rebuild_vault")


async def rebuild() -> int:
    written = 0
    async with SessionLocal() as session:
        accounts = {
            a.id: a
            for a in (await session.execute(select(Account))).scalars().all()
        }
        bookmarks = (
            await session.execute(select(Bookmark).order_by(Bookmark.id))
        ).scalars().all()

        for b in bookmarks:
            account = accounts.get(b.account_id)
            vault.write_bookmark(
                platform=b.platform,
                external_id=b.external_id,
                url=b.url,
                title=b.title,
                text=b.text,
                author_handle=b.author_handle,
                author_name=b.author_name,
                media=b.media_json or [],
                saved_at=b.saved_at,
                fetched_at=b.fetched_at,
                archived=b.archived,
                account_label=account.label if account else None,
            )
            written += 1

    return written


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    n = asyncio.run(rebuild())
    log.info("Wrote %d vault files to %s", n, vault.vault_root().resolve())


if __name__ == "__main__":
    main()
