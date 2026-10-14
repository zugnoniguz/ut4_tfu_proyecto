import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
JOB_TTL_SECONDS = int(os.getenv("STATS_JOB_TTL_SECONDS", "600"))
QUEUE_KEY = "stats:jobs"

# Cliente para la API (respuestas rápidas)
_client = redis.Redis.from_url(
    REDIS_URL, decode_responses=True, socket_connect_timeout=1, socket_timeout=1
)
# Cliente para el trabajador (BRPOP espera bloqueado hasta 5 s)
_worker_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _key(job_id: str) -> str:
    return f"job:{job_id}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(movie_id: int) -> str:
    job_id = uuid.uuid4().hex
    key = _key(job_id)
    pipe = _client.pipeline()
    pipe.hset(key, mapping={"status": "pending", "movie_id": movie_id, "created_at": _now()})
    pipe.expire(key, JOB_TTL_SECONDS)
    pipe.lpush(QUEUE_KEY, job_id)
    pipe.execute()
    return job_id


def get_job(job_id: str) -> dict | None:
    data = _client.hgetall(_key(job_id))
    if not data:
        return None
    if "result" in data:
        data["result"] = json.loads(data["result"])
    return data


def start_worker(process) -> None:
    """Lanza un hilo que toma trabajos de la cola y los procesa con process(movie_id)."""

    def loop():
        while True:
            try:
                item = _worker_client.brpop(QUEUE_KEY, timeout=5)
            except redis.RedisError:
                time.sleep(2)
                continue
            if item is None:
                continue
            _, job_id = item
            key = _key(job_id)
            movie_id = _worker_client.hget(key, "movie_id")
            if movie_id is None:  # el trabajo venció
                continue
            _worker_client.hset(key, "status", "processing")
            try:
                result = process(int(movie_id))
                _worker_client.hset(
                    key, mapping={"status": "done", "result": json.dumps(result), "finished_at": _now()}
                )
            except Exception as e:
                _worker_client.hset(
                    key, mapping={"status": "failed", "error": str(getattr(e, "detail", e))}
                )

    threading.Thread(target=loop, daemon=True, name="stats-worker").start()