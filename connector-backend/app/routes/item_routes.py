from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.database import SessionLocal
from app.dependencies.auth import get_current_user

router = APIRouter(
    tags=["Items"]
)

@router.get("/items")
def get_items(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        items = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).fetchall()

        return [
            dict(row._mapping)
            for row in items
        ]
    finally:
        db.close()