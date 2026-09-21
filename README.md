# TFU – Movies API (microservicios)

Solución de la TFU (UT2 + UT3).

La aplicación se dividió en **3 microservicios** distintos, cada uno su propio app
Python (FastAPI) y su propio contenedor Docker. Los tres comparten un **PostgreSQL**
como backend y están detrás de un **load balancer** (nginx) que enruta y balancea
round-robin hacia cada servicio.

## Arquitectura

```
                   ┌──────────────────────────────────────────────┐
  host 8080 ─────▶ │  gateway / load balancer (nginx)             │
                   │  round-robin + DNS resolve (--scale friendly) │
                   └───────┬──────────────┬───────────────┬────────┘
                           │              │               │
                     stats_backend   reviews_backend  users_backend
                          │              │               │
                   ┌───────▼──────┐┌─────▼───────┐┌─────▼────────┐
                   │ stats-service││ reviews-     ││ users-service│
                   │ (FastAPI)    ││ service      ││ (Basic Auth) │
                   └───────┬──────┘└─────┬───────┘└─────┬────────┘
                           └─────────────┴──────────────┴───────▶ PostgreSQL
```

| Servicio     | Ruta                              | Qué hace                                             |
|--------------|-----------------------------------|------------------------------------------------------|
| stats        | `GET /movies/{id}/stats`          | Agregados de ratings por película (lento 0-3s, queue) |
| reviews      | `GET /movies/{id}/reviews`        | Reviews/ratings de una película                      |
| reviews      | `GET /reviews/{id}`               | Review por ID                                        |
| reviews      | `GET /users/{id}/reviews`         | Reviews de un usuario                                |
| users        | `GET /users/{id}`                 | Info del reviewer (requiere Basic Auth admin)        |

`POSTGRES_USER/PASSWORD/DB = movies/movies/movies`. El esquema + seed se carga una
sola vez al primer arranque desde `postgres/init.sql`. **No hay migraciones** en la
app: cada microservicio asume que la base ya existe.

## Levantado

**Requisitos:** Docker + Docker Compose

```bash
docker compose up --build -d

# verificar
curl http://localhost:8080/gateway/health
curl http://localhost:8080/health
curl http://localhost:8080/movies/1/stats
curl http://localhost:8080/movies/1/reviews
curl http://localhost:8080/reviews/5
curl -u admin:admin123 http://localhost:8080/users/3

# parar
docker compose down -v   # -v elimina también el volumen de postgres
```

### Escalar réplicas (load balancing real)

El LB redescubre réplicas vía DNS de Docker, así que se puede escalar por servicio:

```bash
docker compose up -d --scale stats=3 --scale reviews=3 --scale users=3
curl -s -D- http://localhost:8080/movies/1/reviews -o /dev/null | grep -i x-upstream
# x-upstream varía entre réplicas: 172.x.0.x:8000, ...
```

### Verificar balanceo

Cada respuesta incluye la cabecera `X-Upstream` con la IP del contenedor que
atendió la request.

## Tácticas (UT2)

- **Queue acotada**: `/movies/{id}/stats` es intencionalmente lento y está
  limitado con `limit_req rate=2r/s burst=6` en `gateway/nginx.conf` (devuelve 429).
- **Seguridad**: `/users/{id}` usa HTTP Basic Auth (`admin`/`admin123`) y validación
  de path (`Path(ge=1)`) y queries parametrizadas (psycopg).

## Sin Docker (por microservicio)

```bash
uv run --project services/stats  fastapi dev services/stats/app.py  --port 8001
uv run --project services/reviews fastapi dev services/reviews/app.py --port 8002
uv run --project services/users  fastapi dev services/users/app.py  --port 8003
# apuntando DATABASE_URL a un postgres accesible desde la máquina
```