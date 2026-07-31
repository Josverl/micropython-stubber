from pathlib import Path

from stubber.utils import cache as cache_cfg


def test_clear_all_caches(monkeypatch, tmp_path: Path):
    cache_cfg.get_cache.cache_clear()
    monkeypatch.setattr(cache_cfg, "CACHE_DIR", str(tmp_path))
    caches = [cache_cfg.get_cache(name) for name in ("enrich", "stubgen", "future-cache")]

    try:
        for index, cache in enumerate(caches):
            cache[index] = f"value-{index}"

        assert cache_cfg.clear_all_caches() == 3
        assert all(len(cache) == 0 for cache in caches)
    finally:
        for cache in caches:
            cache.close()
        cache_cfg.get_cache.cache_clear()
