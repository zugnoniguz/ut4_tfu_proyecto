import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://movies:movies@postgres:5432/movies"
)


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def ping() -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False