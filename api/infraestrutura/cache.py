import os, json
from typing import Any, Optional
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

_pool = None
def _get_pool():
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
    return _pool

def _client():
    return redis.Redis(connection_pool=_get_pool())

def ping() -> bool:
    try:
        return _client().ping()
    except Exception:
        return False

def get_json(key: str) -> Optional[Any]:
    raw = _client().get(key)
    if raw is None:
        return None
    return json.loads(raw)

def set_json(key: str, value: Any, ttl_seconds: int = 300) -> None:
    _client().set(key, json.dumps(value), ex=ttl_seconds)
