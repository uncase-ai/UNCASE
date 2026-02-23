"""Lightweight i18n message loader.

Loads JSON catalogs from this package directory and returns translated
strings by key.  Falls back to the key itself when the requested key
or locale is unavailable.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_CATALOG_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=16)
def _load_catalog(locale: str) -> dict[str, str]:
    """Load and cache a JSON message catalog for *locale*."""
    catalog_path = _CATALOG_DIR / f"{locale}.json"
    if not catalog_path.exists():
        return {}
    with catalog_path.open(encoding="utf-8") as fh:
        data: dict[str, str] = json.load(fh)
    return data


def get_message(key: str, locale: str = "es") -> str:
    """Return the translated message for *key* in the given *locale*.

    If the key is missing from the requested locale catalog the function
    falls back to the key string itself so callers always receive a
    displayable value.

    Parameters
    ----------
    key:
        Dot-separated message key, e.g. ``"error.not_found"``.
    locale:
        ISO-639-1 language code.  Defaults to ``"es"``.
    """
    catalog = _load_catalog(locale)
    return catalog.get(key, key)


__all__ = ["get_message"]
