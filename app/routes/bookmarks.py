from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Bookmark
from app.schemas import ArchiveUpdate, BookmarkListOut, BookmarkOut

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=BookmarkListOut)
async def list_bookmarks(
    session: SessionDep,
    platform: str | None = None,
    archived: bool = False,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> BookmarkListOut:
    stmt = select(Bookmark).where(Bookmark.archived == archived)
    count_stmt = select(func.count(Bookmark.id)).where(Bookmark.archived == archived)

    if platform:
        stmt = stmt.where(Bookmark.platform == platform)
        count_stmt = count_stmt.where(Bookmark.platform == platform)

    if q:
        pattern = f"%{q}%"
        cond = (
            Bookmark.title.ilike(pattern)
            | Bookmark.text.ilike(pattern)
            | Bookmark.author_handle.ilike(pattern)
            | Bookmark.author_name.ilike(pattern)
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    stmt = (
        stmt.order_by(Bookmark.saved_at.desc().nullslast(), Bookmark.id.desc())
        .limit(limit)
        .offset(offset)
    )

    items = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(count_stmt)).scalar_one()

    return BookmarkListOut(
        items=[BookmarkOut.model_validate(b) for b in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{bookmark_id}", response_model=BookmarkOut)
async def update_bookmark(
    bookmark_id: int, payload: ArchiveUpdate, session: SessionDep
) -> Bookmark:
    bookmark = await session.get(Bookmark, bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    bookmark.archived = payload.archived
    await session.commit()
    await session.refresh(bookmark)
    return bookmark
