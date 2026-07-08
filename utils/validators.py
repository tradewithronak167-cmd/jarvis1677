"""Validation helpers for HI ROLEX."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import re


SENSITIVE_TERMS: tuple[str, ...] = (
    "password",
    "api key",
    "apikey",
    "access token",
    "token",
    "pin",
    "bank",
    "card number",
    "credit card",
    "debit card",
    "cvv",
    "otp",
    "private key",
    "secret key",
    "seed phrase",
)


def is_safe_path(path: str) -> bool:
    """Return False for empty, system-critical, or suspicious paths."""
    if not path.strip():
        return False
    normalized = str(Path(path).expanduser()).casefold()
    blocked_fragments = (
        "windows\\system32",
        "windows/system32",
        "$recycle.bin",
    )
    return not any(fragment in normalized for fragment in blocked_fragments)


def is_valid_percent(value: object) -> bool:
    """Return True when value is an integer percentage from 0 to 100."""
    try:
        percent = int(value)
    except (TypeError, ValueError):
        return False
    return 0 <= percent <= 100


def is_valid_url(url: str) -> bool:
    """Return True when url has a valid HTTP/HTTPS shape."""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_sensitive_text(text: str) -> bool:
    """Return True when text appears to contain private secrets."""
    lowered = text.casefold()
    if any(term in lowered for term in SENSITIVE_TERMS):
        return True
    return bool(re.search(r"\b(?:\d[ -]?){12,19}\b", text))
