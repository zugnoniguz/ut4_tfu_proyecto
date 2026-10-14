import random
import statistics
import time

import psutil
from datetime import datetime, timezone
from collections import Counter
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from stats_service.db import get_connection, ping

app = FastAPI(
    title="Stats Service",
    description="Estadísticas agregadas de ratings por película (backend Postgres)",
)

_start_time = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str
    cpu_percent: float
    timestamp: str
    uptime: float
    db: str


class MovieInfo(BaseModel):
    id: int
    title: str
    year: int | None = None
    director: str | None = None
    genre: str | None = None


class MovieStatsResponse(BaseModel):
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
    return {"service": "stats", "message": "Hello World"}


@app.get(
    "/health",
    summary="Estado de salud del servicio",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Dependencia crítica caída"}},
)
async def health():
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    db_ok = ping()
    body= HealthResponse(
        status="ok" if db_ok else "down",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cpu_percent=psutil.cpu_percent(),
        uptime=uptime,
        db="ok" if db_ok else "down",
    )
    if not db_ok:
        return JSONResponse(status_code=503, content=body.dict())
    return body


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
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, year, director, genre FROM movies WHERE id = %s",
                (movie_id,),
            )
            movie_row = cur.fetchone()
            if movie_row is None:
                raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

            movie = MovieInfo(
                id=movie_row["id"],
                title=movie_row["title"],
                year=movie_row["year"],
                director=movie_row["director"],
                genre=movie_row["genre"],
            )

            cur.execute(
                "SELECT score FROM ratings WHERE movie_id = %s ORDER BY score",
                (movie_id,),
            )
            scores: list[float] = [float(r["score"]) for r in cur.fetchall()]
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
