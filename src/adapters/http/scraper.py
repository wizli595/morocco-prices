"""Polite HTML scraping helper: robots.txt aware, rate limited."""

import time
import urllib.robotparser
from urllib.parse import urlparse

import httpx
import structlog

from src.core.models.errors import SourceUnavailable

logger = structlog.get_logger()

USER_AGENT = (
    "MaPrix/1.0 (Morocco Price Observatory; research; "
    "+https://github.com/wizli595/morocco-prices)"
)
HEADERS = {"User-Agent": USER_AGENT}
RATE_LIMIT_SECONDS = 2.0

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}
_last_request: dict[str, float] = {}


def _robots(host: str) -> urllib.robotparser.RobotFileParser:
    if host not in _robots_cache:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"https://{host}/robots.txt")
        try:
            parser.read()
        except (OSError, httpx.HTTPError):
            parser.parse([])  # unreachable robots.txt means "allow"
        _robots_cache[host] = parser
    return _robots_cache[host]


def _throttle(host: str) -> None:
    last = _last_request.get(host, 0.0)
    wait = RATE_LIMIT_SECONDS - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    _last_request[host] = time.monotonic()


def fetch_html(url: str, *, source: str = "unknown", timeout: int = 20) -> str:
    """Fetch a page as text, honoring robots.txt and a per-host rate limit."""
    host = urlparse(url).netloc
    if not _robots(host).can_fetch(USER_AGENT, url):
        raise SourceUnavailable(source, f"robots.txt disallows {url}")
    _throttle(host)
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise SourceUnavailable(source, str(exc)) from exc
    return resp.text
