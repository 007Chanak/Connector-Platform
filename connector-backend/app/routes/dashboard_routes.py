from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.database import SessionLocal
from app.dependencies.auth import get_current_user

router = APIRouter(
    tags=["Dashboard"]
)


@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user=Depends(get_current_user)
):

    db = SessionLocal()
    try:

        customers = db.execute(
            text("""
                SELECT COUNT(*)
                FROM unified_customers
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar()

        invoices = db.execute(
            text("""
                SELECT COUNT(*)
                FROM unified_invoices
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar()

        items = db.execute(
            text("""
                SELECT COUNT(*)
                FROM unified_items
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar()

        xero_connected = db.execute(
            text("""
                SELECT COUNT(*)
                FROM integrations
                WHERE tenant_id_fk = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar() > 0

        erpnext_connected = db.execute(
            text("""
                SELECT COUNT(*)
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar() > 0

        

        return {
            "customers": customers,
            "invoices": invoices,
            "items": items,
            "xero_connected": xero_connected,
            "erpnext_connected": erpnext_connected
        }
    finally:
        db.close()

        