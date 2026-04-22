"""Parse raw `Cookie:` header strings pasted from browser DevTools.

We deliberately don't use ``http.cookies.SimpleCookie`` here. Its regex-based
parser is strict about cookie *values* and silently stops at the first value it
considers malformed (e.g. ``g_state={"i_l":0,...}`` which x.com sets). Everything
after that point — including ``auth_token`` and ``ct0`` — would be dropped.

Browsers split the header on ``;`` and take ``name`` / ``value`` around the
first ``=``; we do the same.
"""


def parse_cookie_header(raw: str) -> dict[str, str]:
    """Accept either a bare ``name=value; name=value`` string or one prefixed with ``Cookie:``."""
    if not raw:
        return {}
    text = raw.strip()
    if text.lower().startswith("cookie:"):
        text = text.split(":", 1)[1].strip()

    jar: dict[str, str] = {}
    for part in text.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, _, value = part.partition("=")
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if name:
            jar[name] = value
    return jar


PLATFORM_REQUIRED = {
    "x": ["auth_token", "ct0"],
    "reddit": ["reddit_session"],
}


def extract_required(platform: str, raw_cookies: str) -> dict[str, str]:
    """Pull only the fields a given platform fetcher needs."""
    jar = parse_cookie_header(raw_cookies)
    required = PLATFORM_REQUIRED.get(platform, [])
    missing = [name for name in required if name not in jar]
    if missing:
        raise ValueError(
            f"Missing required cookies for {platform}: {', '.join(missing)}. "
            f"Paste the full Cookie header from DevTools."
        )
    return {k: jar[k] for k in required}
