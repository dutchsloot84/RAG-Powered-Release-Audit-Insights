import json
import time
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def _cache_path(key: str) -> Path:
    sanitized = key.replace("/", "_")
    return CACHE_DIR / f"{sanitized}.json"


def write_cache(key: str, data: Any) -> None:
    path = _cache_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp": time.time(), "data": data}
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def read_cache(key: str, ttl_seconds: Optional[int] = None) -> Optional[Any]:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    ts = payload.get("timestamp", 0)
    if ttl_seconds is not None and ttl_seconds >= 0:
        if time.time() - ts > ttl_seconds:
            return None
    return payload.get("data")
