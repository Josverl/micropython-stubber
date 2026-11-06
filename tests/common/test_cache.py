from pathlib import Path

from diskcache_community import Cache, Disk

from stubber.utils import cache as cache_cfg
from stubber.utils.stubmaker import _stubgen_folder_key, generate_pyi_files


def _planted_stubs(marker: str):
    Path(marker).touch()
    return {"blink.pyi": "def on(pin: str) -> None: ...\n"}


class _PlantedStubs:
    def __init__(self, marker: str):
        self.marker = marker

    def __reduce__(self):
        return _planted_stubs, (self.marker,)


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


def test_stubgen_cache_ignores_planted_pickle(monkeypatch, tmp_path: Path):
    cache_cfg.get_cache.cache_clear()
    monkeypatch.setattr(cache_cfg, "CACHE_ENABLED", True)
    monkeypatch.setattr(cache_cfg, "CACHE_DIR", str(tmp_path / "cache"))
    modules = tmp_path / "frozen"
    modules.mkdir()
    (modules / "blink.py").write_text("def on(pin=2):\n    pass\n")
    marker = tmp_path / "planted-code-ran"
    with Cache(str(tmp_path / "cache" / "stubgen"), disk=Disk) as other_writer:
        other_writer[_stubgen_folder_key(modules)] = _PlantedStubs(str(marker))

    try:
        assert generate_pyi_files(modules)
        assert not marker.exists()
        assert "def on(pin: int = 2)" in (modules / "blink.pyi").read_text()
    finally:
        cache_cfg.get_cache("stubgen").close()
        cache_cfg.get_cache.cache_clear()
