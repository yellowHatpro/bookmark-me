from app.fetchers.base import Fetcher, FetchedItem, FetchResult, AuthError, FetcherError
from app.fetchers.reddit import RedditFetcher
from app.fetchers.x import XFetcher


def get_fetcher(platform: str) -> Fetcher:
    if platform == "x":
        return XFetcher()
    if platform == "reddit":
        return RedditFetcher()
    raise ValueError(f"Unknown platform: {platform}")


__all__ = [
    "AuthError",
    "FetchResult",
    "FetchedItem",
    "Fetcher",
    "FetcherError",
    "RedditFetcher",
    "XFetcher",
    "get_fetcher",
]
