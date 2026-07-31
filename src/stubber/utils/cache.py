"""Shared on-disk cache configuration for stubber.

A single toggle enables/disables **all** stubber disk caches (currently the
codemod "enrich" cache and the frozen "stubgen" cache). Each logical cache lives
in its own sub-directory under a shared base directory.

Environment variables:
    STUBBER_CACHE=0            -> disable all stubber disk caches
    STUBBER_CACHE_DIR=<path>   -> override the base cache location
"""

import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from diskcache import Cache

# Single combined toggle for every stubber disk cache.
CACHE_ENABLED = os.environ.get("STUBBER_CACHE", "1").lower() not in ("0", "false", "no")

# Base directory; each logical cache gets its own sub-directory below this.
CACHE_DIR = os.environ.get("STUBBER_CACHE_DIR", str(Path(tempfile.gettempdir()) / "stubber_cache"))


@lru_cache(maxsize=None)
def get_cache(name: str) -> Cache:
    """Return the shared on-disk cache for the given logical name (created lazily)."""
    cache = Cache(str(Path(CACHE_DIR) / name))
    # Enable hit/miss statistics so `cache_stats()` can report them.
    cache.stats(enable=True)
    return cache


def clear_cache(name: str) -> int:
    """Clear a named cache. Returns the number of removed entries."""
    return get_cache(name).clear()


def clear_all_caches() -> int:
    """Clear every logical cache. Returns the total number of removed entries."""
    cache_dir = Path(CACHE_DIR)
    if not cache_dir.exists():
        return 0

    removed = 0
    for path in cache_dir.iterdir():
        if path.is_dir():
            with Cache(str(path)) as cache:
                removed += cache.clear()
    return removed


def cache_stats(name: str) -> Dict[str, Any]:
    """Return simple statistics about a named cache."""
    cache = get_cache(name)
    hits, misses = cache.stats(enable=True, reset=False)
    return {
        "enabled": CACHE_ENABLED,
        "directory": str(Path(CACHE_DIR) / name),
        "size": len(cache),
        "hits": hits,
        "misses": misses,
    }
