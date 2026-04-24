import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app import vault
from app.config import get_settings
from app.crypto import decrypt_json
from app.db import SessionLocal
from app.fetchers import AuthError, FetcherError, get_fetcher
from app.models import Account, Bookmark, SyncRun

log = logging.getLogger(__name__)


async def run_sync(account_id: int) -> SyncRun:
    """Fetch new items for one account and upsert them. Safe to call concurrently per-account."""
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")

        run = SyncRun(account_id=account.id, started_at=datetime.now(timezone.utc))
        session.add(run)
        await session.flush()

        try:
            new_count = await _do_fetch(session, account)
        except AuthError as exc:
            await _finalize(session, account, run, ok=False, new_count=0, error=str(exc))
            account.status = "reauth_needed"
            account.last_error = str(exc)
            await session.commit()
            return run
        except FetcherError as exc:
            await _finalize(session, account, run, ok=False, new_count=0, error=str(exc))
            account.status = "error"
            account.last_error = str(exc)
            await session.commit()
            return run
        except Exception as exc:  # noqa: BLE001
            log.exception("Unexpected sync failure for account %s", account_id)
            await _finalize(session, account, run, ok=False, new_count=0, error=str(exc))
            account.status = "error"
            account.last_error = str(exc)
            await session.commit()
            return run

        await _finalize(session, account, run, ok=True, new_count=new_count, error=None)
        account.status = "ok"
        account.last_error = None
        account.last_synced_at = run.finished_at
        await session.commit()
        return run


async def _do_fetch(session: AsyncSession, account: Account) -> int:
    settings = get_settings()
    cookies = decrypt_json(account.cookies_encrypted)
    fetcher = get_fetcher(account.platform)

    existing_ids_result = await session.execute(
        select(Bookmark.external_id).where(Bookmark.account_id == account.id)
    )
    known_ids = {row[0] for row in existing_ids_result.all()}

    new_count = 0
    async for item in fetcher.iter_items(
        cookies=cookies,
        extra=account.extra_json or {},
        known_ids=known_ids,
        hard_cap=settings.sync_first_run_hard_cap,
    ):
        stmt = (
            pg_insert(Bookmark)
            .values(
                account_id=account.id,
                platform=item.platform,
                external_id=item.external_id,
                url=item.url,
                title=item.title,
                text=item.text,
                author_handle=item.author_handle,
                author_name=item.author_name,
                media_json=item.media,
                saved_at=item.saved_at,
            )
            .on_conflict_do_nothing(index_elements=["platform", "external_id"])
            .returning(Bookmark.id)
        )
        result = await session.execute(stmt)
        inserted = result.scalar_one_or_none() is not None
        # Mirror to the vault regardless of whether the row was new: title/text
        # can change upstream between syncs, and the vault is our SSoT, so it
        # should always reflect the latest fetch. User notes below `## Notes`
        # are preserved by vault.write_from_item itself.
        try:
            vault.write_from_item(item, account_label=account.label)
        except Exception:
            log.exception(
                "Failed to write vault file for %s/%s", item.platform, item.external_id
            )
        if inserted:
            new_count += 1
            known_ids.add(item.external_id)

    return new_count


async def _finalize(
    session: AsyncSession,
    account: Account,
    run: SyncRun,
    *,
    ok: bool,
    new_count: int,
    error: str | None,
) -> None:
    run.finished_at = datetime.now(timezone.utc)
    run.ok = ok
    run.new_count = new_count
    run.error = error
    session.add(run)
