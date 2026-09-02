# UT2 TFU – Movies API

Solución a la TFU de la UT2.

Se seleccionó la opción 1:
**Gestionar pedidos de trabajo (rendimiento) + dos tácticas de seguridad**.

La aplicación implementa un API REST muy simple de películas/ratings que
demuestra bounded queue con nginx y autenticación/validación con HTTP Basic
Auth.

- `GET /movies/{id}/stats` lento (0-3s) filtrado por cola acotada en
`gateway/nginx.conf` (`limit_req burst=6`).
- `GET /users/{id}` protegido con Basic Auth (`admin/admin123`) y validación de
entrada (`Path(ge=1)`, queries parametrizadas).

## Levantado

**Requisitos:** Docker + Docker Compose

```bash
docker compose up --build -d

# verificar
curl http://localhost:8080/health
curl http://localhost:8080/gateway/health
curl http://localhost:8080/movies/1/stats

# parar
docker compose down
```

**Sin Docker (solo app, sin cola):**
```bash
uv run fastapi dev --port 8000
```
