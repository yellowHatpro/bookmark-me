"""Reddit saved-items fetcher.

Uses the JSON endpoint `old.reddit.com/user/<username>/saved.json` which is the same
thing the old-reddit web UI hits; a valid `reddit_session` cookie is enough.
"""

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings
from app.fetchers.base import AuthError, FetchedItem, Fetcher, FetcherError


class RedditFetcher(Fetcher):
    platform = "reddit"

    async def iter_items(
        self,
        cookies: dict[str, str],
        extra: dict[str, Any],
        known_ids: set[str],
        hard_cap: int,
    ) -> AsyncIterator[FetchedItem]:
        username = extra.get("username")
        if not username:
            raise FetcherError("Reddit account is missing its username; re-add the account.")

        settings = get_settings()
        headers = {
            "User-Agent": settings.reddit_user_agent,
            "Accept": "application/json",
        }
        base = f"https://old.reddit.com/user/{username}/saved.json"

        after: str | None = None
        seen = 0

        async with httpx.AsyncClient(
            headers=headers,
            cookies=cookies,
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            while True:
                params: dict[str, Any] = {"limit": 100, "raw_json": 1}
                if after:
                    params["after"] = after

                resp = await client.get(base, params=params)
                if resp.status_code in (401, 403):
                    raise AuthError(f"Reddit rejected session ({resp.status_code}).")
                if resp.status_code == 429:
                    raise FetcherError("Reddit rate limited us (429). Try again later.")
                if resp.status_code >= 400:
                    raise FetcherError(
                        f"Reddit responded {resp.status_code}: {resp.text[:200]}"
                    )

                payload = resp.json()
                data = payload.get("data") or {}
                children = data.get("children") or []
                if not children:
                    return

                for child in children:
                    kind = child.get("kind")
                    d = child.get("data") or {}
                    item = _to_item(kind, d)
                    if item is None:
                        continue
                    if item.external_id in known_ids:
                        return
                    yield item
                    seen += 1
                    if seen >= hard_cap:
                        return

                after = data.get("after")
                if not after:
                    return


def _to_item(kind: str | None, d: dict[str, Any]) -> FetchedItem | None:
    fullname = d.get("name")  # e.g. "t3_abcd" or "t1_xyz"
    if not fullname:
        return None

    created = d.get("created_utc")
    saved_at = (
        datetime.fromtimestamp(float(created), tz=timezone.utc) if created is not None else None
    )

    permalink = d.get("permalink") or ""
    url = f"https://www.reddit.com{permalink}" if permalink else (d.get("url") or "")
    author = d.get("author")

    if kind == "t3":
        title = d.get("title")
        text = d.get("selftext") or None
        media = _extract_post_media(d)
        return FetchedItem(
            platform="reddit",
            external_id=fullname,
            url=url,
            title=title,
            text=text,
            author_handle=author,
            author_name=author,
            media=media,
            saved_at=saved_at,
        )

    if kind == "t1":
        body = d.get("body")
        link_title = d.get("link_title")
        return FetchedItem(
            platform="reddit",
            external_id=fullname,
            url=url,
            title=link_title,
            text=body,
            author_handle=author,
            author_name=author,
            media=[],
            saved_at=saved_at,
        )

    return None


def _extract_post_media(d: dict[str, Any]) -> list[dict[str, Any]]:
    media: list[dict[str, Any]] = []

    post_hint = d.get("post_hint")
    url_overridden = d.get("url_overridden_by_dest") or d.get("url")

    if post_hint == "image" and url_overridden:
        media.append({"type": "image", "url": url_overridden})
    elif post_hint in ("hosted:video", "rich:video") and url_overridden:
        media.append({"type": "video", "url": url_overridden})

    gallery = d.get("media_metadata")
    if isinstance(gallery, dict):
        for meta in gallery.values():
            src = (meta.get("s") or {}).get("u")
            if src:
                media.append({"type": "image", "url": src.replace("&amp;", "&")})

    return media
