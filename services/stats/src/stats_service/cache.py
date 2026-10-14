import json
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("STATS_CACHE_TTL_SECONDS", "60"))

_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


def _key(movie_id: int) -> str:
    return f"stats:movie:{movie_id}"


def get_cached(movie_id: int) -> tuple[dict | None, bool]:
    """Devuelve (datos, redis_disponible). datos es None si no está en caché."""
    try:
        raw = _client.get(_key(movie_id))
    except redis.RedisError:
        return None, False
    if raw is None:
        return None, True
    return json.loads(raw), True


def set_cached(movie_id: int, data: dict) -> None:
    try:
        _client.setex(_key(movie_id), CACHE_TTL_SECONDS, json.dumps(data))
    except redis.RedisError:
        pass


def ping() -> bool:
    try:
        return bool(_client.ping())
    except redis.RedisError:
        return False