from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

from sqlalchemy import text

from app.database import SessionLocal

SECRET_KEY = "mysecretkey"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("user_id")

        db = SessionLocal()

        user = db.execute(
            text("""
                SELECT *
                FROM users
                WHERE id = :id
            """),
            {
                "id": user_id
            }
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )