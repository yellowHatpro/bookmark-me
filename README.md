# bookmark-me

A personal, local-only aggregator for the posts you save across **X (Twitter)** and
**Reddit**. It signs in with your browser cookies (no paid APIs), syncs on a
schedule, and gives you one searchable feed across platforms.

Personal side-project only. Don't share an instance with people who aren't you — you'd
be handing them your pasted session cookies.

## Stack

- **Backend**: FastAPI + SQLAlchemy (async) + APScheduler, managed with `uv`
- **DB**: Postgres 16
- **Frontend**: Next.js (App Router) + Tailwind, managed with `pnpm`
- **Cookie vault**: Fernet-encrypted JSON blob per account

## Quick start (Docker Compose)

1. Generate a Fernet key and create `.env`:

   ```bash
   cp .env.example .env
   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
   # paste the output as APP_FERNET_KEY=... in .env
   ```

2. Start everything:

   ```bash
   docker compose up --build
   ```

3. Open the UI at <http://localhost:3000> → go to **Settings** → **Add account**.

The API is at <http://localhost:8000> and auto-runs `alembic upgrade head` on startup.

## Repo layout

```
bookmark-me/
├── app/              FastAPI backend package (import as `app`)
├── migrations/       Alembic migrations
├── ui/               Next.js frontend (pnpm)
├── scripts/          serve-db.sh / serve-api.sh / serve-ui.sh
├── alembic.ini
├── main.py           root entry point (`python main.py`)
├── pyproject.toml    backend project (managed by uv)
├── uv.lock
├── Dockerfile        backend image
├── compose.yaml
└── .env / .env.example
```

## Local dev without Docker

Two scripts. Run `setup.sh` once per clone, then `dev.sh` every day.

```bash
./scripts/setup.sh     # .env + Fernet key, start db, uv sync, migrate, pnpm install
./scripts/dev.sh       # starts db + backend (:8000) + frontend (:3000)
```

`setup.sh` is idempotent — re-running it skips steps that are already done
(existing `.env`, existing key, already-installed deps).

### Manual equivalents

```bash
docker compose up -d db
set -a; source .env; set +a
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

cd ui && pnpm install && pnpm dev
```

## Getting your cookies

You only need to do this once per account; the app will tell you when cookies expire
(status flips to **re-auth needed** on the Settings page).

### X (Twitter)

Required fields: `auth_token`, `ct0`.

1. Open <https://x.com/i/bookmarks> in a logged-in browser.
2. Open DevTools (F12) → **Network** tab.
3. Refresh the page. Click the first `Bookmarks` XHR request.
4. Scroll the Headers panel to **Request Headers** → **Cookie**.
5. Right-click → **Copy value**, and paste the whole thing into the Settings form.

The backend only keeps `auth_token` and `ct0` — everything else is discarded.

### Reddit

Required fields: `reddit_session`. You also need to enter your Reddit username
(without the `u/`), because the fetcher calls
`old.reddit.com/user/<you>/saved.json`.

1. Open <https://www.reddit.com> in a logged-in browser.
2. Open DevTools (F12) → **Application** tab → **Cookies** → `https://www.reddit.com`.
3. Copy the full Cookie header from any request (Network tab → Headers → Cookie) and
   paste into the Settings form. The backend extracts just `reddit_session`.

## How the fetchers work (no official APIs)

Each fetcher hits the same internal endpoint the web UI uses, with the session
cookies you pasted.

- **X** — `GET x.com/i/api/graphql/<queryId>/Bookmarks` with
  `Authorization: Bearer <public web bearer>` + `X-CSRF-Token: <ct0>`. The `queryId`
  rotates every few months; we keep a known-good value in `config.py` and do a
  best-effort resolve from the live `main.<hash>.js` bundle on each run. When X
  changes their schema or flags, surface it by setting `X_BOOKMARKS_QUERY_ID` in
  `.env`.
- **Reddit** — `GET old.reddit.com/user/<you>/saved.json?limit=100&after=<cursor>`
  with your `reddit_session` cookie and a distinctive `User-Agent`.

Each run paginates newest-first and stops as soon as it hits an `external_id` that's
already stored — so steady-state syncs are cheap.

## Project layout

```
bookmark-me/
  compose.yaml
  .env.example
  backend/
    pyproject.toml         # uv-managed
    alembic.ini
    Dockerfile
    migrations/
    src/app/
      main.py              # FastAPI + lifespan starts the scheduler
      config.py
      db.py
      models.py            # Account, Bookmark, SyncRun
      crypto.py            # Fernet wrap/unwrap
      cookie_parser.py     # parse pasted Cookie: header
      schemas.py
      scheduler.py         # APScheduler in-process
      sync_service.py      # orchestrates one sync run
      routes/
        accounts.py        # CRUD + cookie paste + sync-now
        bookmarks.py       # list/search/archive
      fetchers/
        base.py
        x.py
        reddit.py
  frontend/
    Dockerfile
    src/
      app/
        page.tsx           # feed
        settings/page.tsx  # account management
      components/ui.tsx
      lib/api.ts
```

## Adding another platform later

All the plumbing is generic; for a new platform you only need to:

1. Add a fetcher in `backend/src/app/fetchers/` that implements the `Fetcher`
   protocol from `base.py` (yields `FetchedItem`s, raises `AuthError` on 401/403).
2. Register it in `app/fetchers/__init__.py` and extend `PLATFORM_REQUIRED` in
   `cookie_parser.py`.
3. Add the new literal to `Platform` in `schemas.py` and to the frontend's platform
   `<select>` options.

Candidates to try next, in rough order of difficulty:

- **LinkedIn saved posts** — needs `li_at` + `JSESSIONID` (doubles as CSRF); Voyager
  endpoint `www.linkedin.com/voyager/api/feed/savedItems`. Fragile; may need a
  Playwright fallback when challenged.
- **Google Keep** — no cookie endpoint. Easiest path is `gkeepapi` with a
  gpsoauth-issued master token (different auth model from the other platforms).
- **Instagram saved / YouTube "Watch Later"** — same cookie-based pattern.

## Troubleshooting

- **`APP_FERNET_KEY is not set`** — you skipped step 1. Generate a key and put it in
  `.env`.
- **X fetcher returns 404** — queryId has rotated. Copy the new value from the
  `main.*.js` bundle and set `X_BOOKMARKS_QUERY_ID` in `.env`.
- **Reddit returns 429** — you shared the `User-Agent` with too many requests. Wait a
  few minutes; consider bumping `SYNC_INTERVAL_MIN`.
- **Status stuck on `reauth_needed`** — paste a fresh Cookie header via the Settings
  page's "Update existing" flow.

## License

Personal project, no license granted. Use at your own risk; respect each platform's
terms of service.
