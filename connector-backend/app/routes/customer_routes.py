from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.database import SessionLocal
from app.dependencies.auth import get_current_user

router = APIRouter(
    tags=["Customers"]
)

@router.get("/customers")
def get_customers(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        customers = db.execute(
            text("""
                SELECT *
                FROM unified_customers
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).fetchall()

        return [
            dict(row._mapping)
            for row in customers
        ]
    finally:
        db.close()