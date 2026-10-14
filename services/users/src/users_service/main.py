import psutil
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException, Path
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from users_service.db import get_connection, ping

app = FastAPI(
    title="Users Service",
    description="Información de reviewers/usuarios y sus agregados de ratings (backend Postgres)",
)

_start_time = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str
    cpu_percent: float
    timestamp: str
    uptime: float
    db: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    created_at: str
    rating_count: int
    rating_average: float


@app.get("/")
async def root():
    return {"service": "users", "message": "Hello World"}


@app.get(
    "/health",
    summary="Estado de salud del servicio",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Dependencia crítica caída"}},
)
def health():
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    db_ok = ping()
    body = HealthResponse(
        status="ok" if db_ok else "down",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cpu_percent=psutil.cpu_percent(),
        uptime=uptime,
        db="ok" if db_ok else "down",
    )
    if not db_ok:
        return JSONResponse(status_code=503, content=body.model_dump())
    return body


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obtener información de un usuario por ID (admin)",
    description="La autenticación la realiza el gateway (Gateway Offloading).",
)
async def get_user(
    user_id: int = Path(..., ge=1, description="ID del usuario"),
    authenticated_user: str = Header(..., alias="X-Authenticated-User"),
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, display_name, created_at FROM reviewers WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")

            cur.execute(
                "SELECT COUNT(id) AS rating_count, AVG(score) AS rating_average "
                "FROM ratings WHERE reviewer_id = %s",
                (user_id,),
            )
            agg = cur.fetchone()
            rating_count = int(agg["rating_count"] or 0)
            rating_average = (
                round(float(agg["rating_average"]), 2)
                if agg["rating_average"] is not None
                else 0.0
            )

            created_at = row["created_at"]
            if not isinstance(created_at, str):
                created_at = created_at.isoformat()

            return UserResponse(
                id=row["id"],
                username=row["username"],
                display_name=row["display_name"],
                created_at=created_at,
                rating_count=rating_count,
                rating_average=rating_average,
            )
