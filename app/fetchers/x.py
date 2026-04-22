"""X (Twitter) bookmarks fetcher.

Hits the same GraphQL endpoint the x.com web app uses. The `queryId` portion of the
URL rotates every few months; we keep a known-good value in config and try a
best-effort resolver from the current web bundle before giving up.
"""

import json
import logging
import re
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

import httpx
from dateutil import parser as dtparser

from app.config import get_settings
from app.fetchers.base import AuthError, FetchedItem, Fetcher, FetcherError

log = logging.getLogger(__name__)


# Feature flags the web client currently sends. We copy a conservative set that the
# Bookmarks endpoint accepts; if X adds a required flag, the response carries an
# explicit error telling us which one.
_FEATURES = {
    "graphql_timeline_v2_bookmark_timeline": True,
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
}


class XFetcher(Fetcher):
    platform = "x"

    async def iter_items(
        self,
        cookies: dict[str, str],
        extra: dict[str, Any],
        known_ids: set[str],
        hard_cap: int,
    ) -> AsyncIterator[FetchedItem]:
        settings = get_settings()
        ct0 = cookies.get("ct0")
        auth = cookies.get("auth_token")
        if not ct0 or not auth:
            raise FetcherError("X account is missing auth_token/ct0; paste fresh cookies.")

        headers = {
            "authorization": f"Bearer {settings.x_web_bearer}",
            "x-csrf-token": ct0,
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "content-type": "application/json",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://x.com",
            "referer": "https://x.com/i/bookmarks",
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        async with httpx.AsyncClient(
            headers=headers,
            cookies={"auth_token": auth, "ct0": ct0},
            timeout=30.0,
            follow_redirects=False,
        ) as client:
            query_id = await _resolve_query_id(
                cookies={"auth_token": auth, "ct0": ct0},
                user_agent=headers["user-agent"],
                fallback=settings.x_bookmarks_query_id,
            )
            log.info("X bookmarks fetch using queryId=%s", query_id)

            cursor: str | None = None
            seen = 0

            while True:
                payload = await _call_bookmarks(client, query_id, cursor)
                entries = _extract_entries(payload)
                if not entries:
                    return

                next_cursor: str | None = None
                produced_any = False

                for entry in entries:
                    entry_id = entry.get("entryId", "")
                    if entry_id.startswith("cursor-bottom-"):
                        next_cursor = _cursor_value(entry)
                        continue
                    if entry_id.startswith("cursor-top-"):
                        continue

                    item = _entry_to_item(entry)
                    if item is None:
                        continue
                    if item.external_id in known_ids:
                        return
                    yield item
                    produced_any = True
                    seen += 1
                    if seen >= hard_cap:
                        return

                if not next_cursor or not produced_any:
                    return
                cursor = next_cursor


async def _call_bookmarks(
    client: httpx.AsyncClient, query_id: str, cursor: str | None
) -> dict[str, Any]:
    variables: dict[str, Any] = {"count": 100, "includePromotedContent": False}
    if cursor:
        variables["cursor"] = cursor

    url = f"https://x.com/i/api/graphql/{query_id}/Bookmarks"
    resp = await client.get(
        url,
        params={
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(_FEATURES, separators=(",", ":")),
        },
    )
    if resp.status_code in (401, 403):
        raise AuthError(f"X rejected session ({resp.status_code}). Paste fresh cookies.")
    if resp.status_code == 429:
        raise FetcherError("X rate limited us (429). Try again later.")
    if resp.status_code == 404:
        raise FetcherError(
            "X returned 404 for Bookmarks queryId; it has rotated. "
            "Set X_BOOKMARKS_QUERY_ID in .env to the current value."
        )
    if resp.status_code in (301, 302, 303, 307, 308):
        # X redirects unauthenticated requests to login HTML. Treat as auth failure.
        raise AuthError(
            f"X redirected to {resp.headers.get('location', '?')}; session is not accepted. "
            "Paste fresh cookies (make sure auth_token and ct0 are both current)."
        )
    if resp.status_code >= 400:
        raise FetcherError(f"X responded {resp.status_code}: {resp.text[:200]}")

    content_type = resp.headers.get("content-type", "")
    if "json" not in content_type.lower():
        snippet = resp.text[:300].replace("\n", " ")
        # A 200 HTML response almost always means an auth/interstitial page
        # (X serves the SPA shell when it doesn't like the session).
        if "<html" in snippet.lower() or "<!doctype" in snippet.lower():
            raise AuthError(
                "X returned an HTML page instead of JSON (likely auth/interstitial). "
                "Your cookies are probably stale — paste a fresh Cookie header. "
                f"[status={resp.status_code}, content-type={content_type!r}]"
            )
        raise FetcherError(
            f"X returned non-JSON body (status={resp.status_code}, "
            f"content-type={content_type!r}): {snippet!r}"
        )

    try:
        body = resp.json()
    except ValueError as exc:
        snippet = resp.text[:300].replace("\n", " ")
        raise FetcherError(
            f"X response wasn't valid JSON despite {content_type!r}: {snippet!r}"
        ) from exc

    if isinstance(body, dict) and body.get("errors"):
        raise FetcherError(f"X GraphQL errors: {body['errors']}")
    return body


async def _resolve_query_id(
    *, cookies: dict[str, str], user_agent: str, fallback: str
) -> str:
    """Best-effort: scrape x.com's web bundle for the current Bookmarks queryId.

    Uses a plain browser-like client (no API headers). The authed client used for the
    GraphQL call must NOT be reused here, because x.com returns 401 for HTML routes
    when Bearer/OAuth2 headers are present.
    """
    browser_headers = {
        "user-agent": user_agent,
        "accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "accept-language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(
            headers=browser_headers,
            cookies=cookies,
            timeout=15.0,
            follow_redirects=True,
        ) as web:
            index = await web.get("https://x.com/i/bookmarks")
            if index.status_code >= 400:
                log.info(
                    "queryId resolver: /i/bookmarks returned %s; using fallback",
                    index.status_code,
                )
                return fallback
            m = re.search(
                r'https://abs\.twimg\.com/responsive-web/client-web/main\.[\w]+\.js',
                index.text,
            )
            if not m:
                log.info("queryId resolver: couldn't locate main.*.js URL; using fallback")
                return fallback
            bundle = await web.get(m.group(0))
            if bundle.status_code >= 400:
                log.info("queryId resolver: bundle returned %s; using fallback", bundle.status_code)
                return fallback
            match = re.search(
                r'queryId:"([A-Za-z0-9_-]+)"[^}]*operationName:"Bookmarks"', bundle.text
            )
            if match:
                return match.group(1)
            match = re.search(
                r'operationName:"Bookmarks"[^}]*queryId:"([A-Za-z0-9_-]+)"', bundle.text
            )
            if match:
                return match.group(1)
            log.info("queryId resolver: Bookmarks operation not found in bundle; using fallback")
    except Exception as exc:
        log.info("queryId resolver failed (%s); using fallback.", exc)
    return fallback


def _extract_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        timeline = (
            payload["data"]["bookmark_timeline_v2"]["timeline"]["instructions"]
        )
    except (KeyError, TypeError):
        return []
    for instr in timeline:
        if instr.get("type") == "TimelineAddEntries":
            return instr.get("entries") or []
    return []


def _cursor_value(entry: dict[str, Any]) -> str | None:
    content = entry.get("content") or {}
    return content.get("value")


def _entry_to_item(entry: dict[str, Any]) -> FetchedItem | None:
    content = entry.get("content") or {}
    if content.get("entryType") != "TimelineTimelineItem":
        return None
    item_content = content.get("itemContent") or {}
    if item_content.get("itemType") != "TimelineTweet":
        return None
    results = (item_content.get("tweet_results") or {}).get("result") or {}
    if results.get("__typename") == "TweetWithVisibilityResults":
        results = results.get("tweet") or {}

    legacy = results.get("legacy") or {}
    rest_id = results.get("rest_id") or legacy.get("id_str")
    if not rest_id:
        return None

    user_legacy = (
        ((results.get("core") or {}).get("user_results") or {}).get("result") or {}
    ).get("legacy") or {}
    handle = user_legacy.get("screen_name")
    name = user_legacy.get("name")

    full_text = legacy.get("full_text") or ""
    note = results.get("note_tweet") or {}
    if note:
        note_result = (note.get("note_tweet_results") or {}).get("result") or {}
        full_text = note_result.get("text") or full_text

    created_at = legacy.get("created_at")
    saved_at: datetime | None = None
    if created_at:
        try:
            saved_at = dtparser.parse(created_at)
        except (ValueError, TypeError):
            saved_at = None

    media: list[dict[str, Any]] = []
    extended = (legacy.get("extended_entities") or {}).get("media") or []
    for m in extended:
        mtype = m.get("type")
        murl = m.get("media_url_https") or m.get("media_url")
        if not murl:
            continue
        if mtype == "photo":
            media.append({"type": "image", "url": murl})
        elif mtype in ("video", "animated_gif"):
            variants = (m.get("video_info") or {}).get("variants") or []
            mp4s = [
                v for v in variants if v.get("content_type") == "video/mp4" and v.get("bitrate")
            ]
            best = max(mp4s, key=lambda v: v.get("bitrate", 0)) if mp4s else None
            media.append({
                "type": "video",
                "url": best["url"] if best else murl,
                "poster": murl,
            })

    url = f"https://x.com/{handle}/status/{rest_id}" if handle else f"https://x.com/i/status/{rest_id}"

    return FetchedItem(
        platform="x",
        external_id=rest_id,
        url=url,
        title=None,
        text=full_text or None,
        author_handle=handle,
        author_name=name,
        media=media,
        saved_at=saved_at,
    )
