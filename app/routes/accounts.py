from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cookie_parser import extract_required
from app.crypto import encrypt_json
from app.db import get_session
from app.models import Account
from app.schemas import AccountCreate, AccountOut, SyncRunOut
from app.scheduler import scheduler
from app.sync_service import run_sync

router = APIRouter(prefix="/accounts", tags=["accounts"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[AccountOut])
async def list_accounts(session: SessionDep) -> list[Account]:
    result = await session.execute(select(Account).order_by(Account.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate, session: SessionDep, background: BackgroundTasks
) -> Account:
    try:
        cookies = extract_required(payload.platform, payload.raw_cookies)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extra: dict = {}
    if payload.platform == "reddit":
        if not payload.username:
            raise HTTPException(
                status_code=400,
                detail="Reddit accounts require a username (to hit /user/<name>/saved.json).",
            )
        extra["username"] = payload.username.strip().lstrip("u/").lstrip("/")

    account = Account(
        platform=payload.platform,
        label=payload.label,
        cookies_encrypted=encrypt_json(cookies),
        extra_json=extra,
        status="ok",
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)

    scheduler.schedule_account(account.id)
    background.add_task(run_sync, account.id)
    return account


@router.put("/{account_id}/cookies", response_model=AccountOut)
async def update_cookies(
    account_id: int,
    payload: AccountCreate,
    session: SessionDep,
    background: BackgroundTasks,
) -> Account:
    account = await session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.platform != payload.platform:
        raise HTTPException(status_code=400, detail="Platform mismatch")

    try:
        cookies = extract_required(payload.platform, payload.raw_cookies)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    account.cookies_encrypted = encrypt_json(cookies)
    account.label = payload.label
    if payload.platform == "reddit" and payload.username:
        account.extra_json = {
            **(account.extra_json or {}),
            "username": payload.username.strip().lstrip("u/").lstrip("/"),
        }
    account.status = "ok"
    account.last_error = None
    await session.commit()
    await session.refresh(account)

    background.add_task(run_sync, account.id)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, session: SessionDep) -> None:
    account = await session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    scheduler.unschedule_account(account_id)
    await session.delete(account)
    await session.commit()


@router.post("/{account_id}/sync", response_model=SyncRunOut)
async def sync_now(account_id: int, session: SessionDep) -> object:
    account = await session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    run = await run_sync(account_id)
    return run
