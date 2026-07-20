"""Shared HTTP client with retries and timeout."""

import time
from typing import Any, cast

import httpx
import structlog

from src.core.models.errors import SourceUnavailable

logger = structlog.get_logger()

DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
RETRY_DELAY = 5
USER_AGENT = "MaPrix/1.0 (Morocco Price Observatory; Academic Research)"

HEADERS = {"User-Agent": USER_AGENT}


def fetch_json(
    url: str,
    *,
    params: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    source: str = "unknown",
) -> dict[str, Any] | list[Any]:
    """GET a URL and return parsed JSON with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            resp = httpx.get(url, params=params, timeout=timeout, headers=HEADERS)
            resp.raise_for_status()
            return cast("dict[str, Any] | list[Any]", resp.json())
        except httpx.HTTPStatusError as e:
            logger.warning(
                "http.status_error",
                source=source,
                url=url,
                status=e.response.status_code,
                attempt=attempt,
            )
            if attempt == retries:
                raise SourceUnavailable(source, str(e)) from e
        except httpx.RequestError as e:
            logger.warning(
                "http.request_error",
                source=source,
                url=url,
                error=str(e),
                attempt=attempt,
            )
            if attempt == retries:
                raise SourceUnavailable(source, str(e)) from e
        time.sleep(RETRY_DELAY)

    raise SourceUnavailable(source, "max retries exceeded")


def download_bytes(
    url: str,
    *,
    timeout: int = 120,
    source: str = "unknown",
) -> bytes:
    """Download raw bytes from a URL."""
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True, headers=HEADERS)
        resp.raise_for_status()
        return resp.content
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        raise SourceUnavailable(source, str(e)) from e
