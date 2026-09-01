from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel

import psutil

app = FastAPI()
_start_time = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str
    cpu_percent: float
    timestamp: str
    uptime: float


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/health",
    summary="Estado de salud del servicio",
    response_model=HealthResponse,
    description="Devuelve el estado de salud del servicio, incluyendo su uptime y datos de cpu de la máquina"
)
async def health():
    """Devuelve el estado actual del servicio.
    """
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cpu_percent=psutil.cpu_percent(),
        uptime=uptime,
    )
