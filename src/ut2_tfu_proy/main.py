import psutil
import random
import statistics
import time

from collections import Counter
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

from ut2_tfu_proy.users import router as users_router

app = FastAPI(
    title="UT2 TFU Movies API",
    description="API de películas y ratings",
)

app.include_router(users_router)

_start_time = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str
    cpu_percent: float
    timestamp: str
    uptime: float


class MovieInfo(BaseModel):
    id: int
    title: str
    year: int | None = None
    director: str | None = None
    genre: str | None = None


class MovieStatsResponse(BaseModel):
    """Stats for a single movie based on its reviews/ratings."""

    movie: MovieInfo
    rating_count: int
    avg_rating: float | None
    min_rating: float | None
    max_rating: float | None
    median_rating: float | None
    stddev: float | None
    stddev_rating: float | None
    score_distribution: dict[str, int]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/health",
    summary="Estado de salud del servicio",
    response_model=HealthResponse,
    description="Devuelve el estado de salud del servicio, incluyendo su uptime y datos de cpu de la máquina",
)
async def health():
    """Devuelve el estado actual del servicio."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cpu_percent=psutil.cpu_percent(),
        uptime=uptime,
    )


def _get_connection():
    """Lazy import to avoid circular import at module load."""
    from init_db import get_connection as _gc, init_db

    try:
        init_db()
    except Exception:
        pass
    return _gc()


@app.get(
    "/movies/{movie_id}/stats",
    response_model=MovieStatsResponse,
    summary="Estadísticas de una película",
    description=(
        "Dado un ID de película, devuelve estadísticas agregadas sobre sus reviews/ratings: "
        "cantidad, promedio, mínimo, máximo, mediana, desvío estándar y distribución de puntajes."
    ),
)
async def movie_stats(
    movie_id: int = Path(..., ge=1, description="ID de la película"),
):
    conn = _get_connection()
    try:
        movie_row = conn.execute(
            "SELECT id, title, year, director, genre FROM movies WHERE id = ?",
            (movie_id,),
        ).fetchone()
        if movie_row is None:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

        movie = MovieInfo(
            id=movie_row["id"],
            title=movie_row["title"],
            year=movie_row["year"],
            director=movie_row["director"],
            genre=movie_row["genre"],
        )

        rows = conn.execute(
            "SELECT score FROM ratings WHERE movie_id = ? ORDER BY score",
            (movie_id,),
        ).fetchall()
        scores: list[float] = [float(r["score"]) for r in rows]
        count = len(scores)

        if count == 0:
            avg = None
            min_r = None
            max_r = None
            median = None
            std = None
            distribution: dict[str, int] = {}
        else:
            avg = round(statistics.fmean(scores), 2)
            min_r = min(scores)
            max_r = max(scores)
            median = round(statistics.median(scores), 2)
            if count >= 2:
                try:
                    std = round(statistics.pstdev(scores), 2)
                except statistics.StatisticsError:
                    std = 0.0
            else:
                std = 0.0

            dist_counter = Counter(int(s // 1) for s in scores)
            distribution = {str(k): v for k, v in sorted(dist_counter.items())}

        time.sleep(random.random() * 3)
        return MovieStatsResponse(
            movie=movie,
            rating_count=count,
            avg_rating=avg,
            min_rating=min_r,
            max_rating=max_r,
            median_rating=median,
            stddev=std,
            stddev_rating=std,
            score_distribution=distribution,
        )
    finally:
        conn.close()
