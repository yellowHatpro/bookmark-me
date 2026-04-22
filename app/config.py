from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Known-good Bookmarks queryId. Rotates occasionally; the resolver tries to refresh from
# the live web bundle, and `X_BOOKMARKS_QUERY_ID` in .env can override it when X breaks.
_DEFAULT_X_BOOKMARKS_QUERY_ID = "j5KExFXtSWj8HjRui17ydA"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://bookmark:bookmark@localhost:5432/bookmark"
    app_fernet_key: str = ""
    sync_interval_min: int = 15
    sync_first_run_hard_cap: int = 2000
    cors_origins: str = "http://localhost:3000"

    # X internal web bearer token. Public, ships in x.com web bundle; stable for years.
    x_web_bearer: str = (
        "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D"
        "1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )
    x_bookmarks_query_id: str = _DEFAULT_X_BOOKMARKS_QUERY_ID

    reddit_user_agent: str = "bookmark-me/0.1 (personal sync)"

    @field_validator("x_bookmarks_query_id", mode="before")
    @classmethod
    def _fallback_query_id(cls, v: str | None) -> str:
        # An empty string from .env (e.g. `X_BOOKMARKS_QUERY_ID=`) should not wipe the
        # hardcoded default. Only an explicit non-empty value overrides it.
        return v or _DEFAULT_X_BOOKMARKS_QUERY_ID

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
