from app.cache import cache_manager


def test_cache_ttl(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_manager, "CACHE_DIR", tmp_path)
    cache_manager.write_cache("key", {"v": 1})
    assert cache_manager.read_cache("key", ttl_seconds=100)["v"] == 1
    assert cache_manager.read_cache("key", ttl_seconds=0) is None
