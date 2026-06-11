from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.database import SessionLocal
from app.dependencies.auth import get_current_user

router = APIRouter(
    tags=["Invoices"]
)

@router.get("/invoices")
def get_invoices(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        invoices = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).fetchall()

        return [
            dict(row._mapping)
            for row in invoices
        ]
    finally:
        db.close()