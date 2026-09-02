import secrets

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

security = HTTPBasic()


def _verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify hard-coded admin username/password via HTTP Basic Auth."""
    username_ok = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _get_connection():
    from init_db import get_connection as _gc, init_db

    try:
        init_db()
    except Exception:
        pass
    return _gc()


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    created_at: str
    rating_count: int


router = APIRouter()


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obtener información de un usuario por ID (admin)",
    description="Devuelve la información de un reviewer/usuario dado su ID. Requiere autenticación Basic con usuario y contraseña de admin hard-codeados.",
)
async def get_user(
    user_id: int = Path(..., ge=1, description="ID del usuario"),
    admin: str = Depends(_verify_admin),
):
    conn = _get_connection()
    try:
        row = conn.execute(
            """SELECT
                re.id AS id,
                re.username AS username,
                re.display_name AS display_name,
                re.created_at AS created_at,
                COUNT(ra.id) AS rating_count
                FROM reviewers re
                JOIN ratings ra ON ra.reviewer_id = re.id
                WHERE re.id = ?
                """,
            (user_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return UserResponse(
            id=row["id"],
            username=row["username"],
            display_name=row["display_name"],
            created_at=row["created_at"],
            rating_count=row["rating_count"],
        )
    finally:
        conn.close()
