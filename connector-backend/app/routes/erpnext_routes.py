from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.auth import (
    get_current_user
)

from app.services.erpnext_to_xero_sync import (
    sync_erpnext_to_xero
)

from app.services.erpnext_invoice_sync_service import (
    sync_erpnext_invoices_service
)

from app.services.unified_to_erpnext.invoices import (
    push_invoices_to_erpnext
)

from app.services.erpnext_item_service import (
    fetch_erpnext_complete_items
)

from app.services.erpnext_to_unified.items import (
    sync_erpnext_items_service
)

from app.services.unified_to_erpnext.items import (
    push_items_to_erpnext
)

from app.services.erpnext_to_unified.customers import (
    sync_erpnext_customers_service
)

from app.services.unified_to_erpnext.customers import (
    push_customers_to_erpnext
)

from app.services.erpnext_to_unified.suppliers import (
    fetch_complete_erpnext_suppliers
)

from app.services.erpnext_to_unified.suppliers import (
    sync_erpnext_suppliers_service
)

from app.services.unified_to_erpnext.suppliers import (
    push_suppliers_to_erpnext
)

from app.services.erpnext_to_unified.bills import (
    fetch_complete_erpnext_bills,
    sync_erpnext_bills_service
)

from app.services.unified_to_erpnext.bills import (
    push_bills_to_erpnext
)

from app.services.erpnext_to_unified.purchase_orders import (
    sync_erpnext_purchase_orders_service
)

from app.services.unified_to_erpnext.purchase_orders import (
    push_purchase_orders_to_erpnext
)

from app.services.erpnext_to_unified.sales_orders import (
    sync_erpnext_sales_orders_service
)

from app.services.unified_to_erpnext.sales_orders import (
    push_sales_orders_to_erpnext
)

from app.services.erpnext_to_unified.accounts import (
    sync_erpnext_accounts_service
)


from sqlalchemy import text
from app.database import SessionLocal
import requests

router = APIRouter(tags=["ERPNext"])


@router.post("/erpnext/connect")
def connect_erpnext(

    erp_url: str,
    api_key: str,
    api_secret: str,

    current_user = Depends(get_current_user)
):

    db = SessionLocal()

    try:

        print("ERP CONNECT HIT")
        print("USER:", current_user.id)
        print("TENANT:", current_user.tenant_id)

        db.execute(
            text("""
                INSERT INTO erpnext_integrations
                (
                    user_id,
                    tenant_id,
                    erp_url,
                    api_key,
                    api_secret
                )
                VALUES
                (
                    :user_id,
                    :tenant_id,
                    :erp_url,
                    :api_key,
                    :api_secret
                )
            """),
            {
                "user_id": current_user.id,
                "tenant_id": current_user.tenant_id,
                "erp_url": erp_url,
                "api_key": api_key,
                "api_secret": api_secret
            }
        )

        print("INSERTING ERP RECORD")

        db.commit()

        print("COMMIT DONE")

        return {
            "message": "ERPNext connected successfully"
        }

    finally:
        db.close()


@router.get("/erpnext/customers")
def get_customers(

    current_user = Depends(get_current_user)
):

    db = SessionLocal()
    try:

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).fetchone()

        if not erp:
            return {
                "error": "No ERPNext integration found"
            }

        url = f"{erp.erp_url}/api/resource/Customer"

        headers = {
            "Authorization": (
                f"token {erp.api_key}:{erp.api_secret}"
            )
        }

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()
    finally:
        db.close()


@router.get("/erpnext/push-customers")
def push_customers(

    current_user = Depends(get_current_user)
):

    return push_customers_to_erpnext(
        current_user.id,
        current_user.tenant_id
    )


@router.get("/sync/erpnext/xero")
def sync_erpnext_xero(
    current_user = Depends(get_current_user)
):

    return sync_erpnext_to_xero(
        current_user.id,
        current_user.tenant_id
    )

@router.get(
    "/sync/erpnext/invoices"
)
def sync_erpnext_invoices(
    current_user=Depends(
        get_current_user
    )
):

    return sync_erpnext_invoices_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/invoices/erpnext")
def sync_invoices_to_erpnext(
    current_user=Depends(
        get_current_user
    )
):

    return push_invoices_to_erpnext(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/erpnext/items")
def get_erpnext_items(
    current_user=Depends(
        get_current_user
    )
):

    return fetch_erpnext_complete_items(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/erpnext/items")
def sync_erpnext_items(
    current_user=Depends(
        get_current_user
    )
):

    return sync_erpnext_items_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/items/erpnext")
def sync_items_to_erpnext(
    current_user=Depends(
        get_current_user
    )
):

    return push_items_to_erpnext(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/erpnext/customers")
def sync_erpnext_customers(
    current_user=Depends(
        get_current_user
    )
):

    return sync_erpnext_customers_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/suppliers")
def get_suppliers(
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    try:
        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": current_user.id}
        ).scalar()

        suppliers = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE tenant_id = :tenant_id
            """),
            {"tenant_id": tenant_id}
        ).mappings().all()

        return suppliers

    finally:
        db.close()

@router.get("/sync/erpnext/suppliers")
def sync_erpnext_suppliers(
    current_user=Depends(get_current_user)
):
    return sync_erpnext_suppliers_service(
        current_user.id,
        None
    )

@router.get("/push/suppliers/erpnext")
def push_suppliers(
    current_user=Depends(get_current_user)
):
    return push_suppliers_to_erpnext(
        current_user.id,
        None
    )

@router.get("/bills")
def get_bills(
    current_user=Depends(get_current_user)
):

    db = SessionLocal()

    try:

        bills = db.execute(
            text("""
                SELECT *
                FROM unified_bills
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().all()

        return bills

    finally:
        db.close()

@router.get("/test-bills")
def test_bills(
    current_user=Depends(get_current_user)
):
    return fetch_complete_erpnext_bills(
        current_user.id,
        None
    )

@router.get("/sync/erpnext/bills")
def sync_erpnext_bills(
    current_user=Depends(get_current_user)
):

    return sync_erpnext_bills_service(
        current_user.id,
        current_user.tenant_id
    )

@router.post("/push/bills/erpnext")
def migrate_bills_xero_to_erpnext(
    current_user=Depends(get_current_user)
):

    return push_bills_to_erpnext(
        user_id=current_user.id,
        tenant_id=None
    )

@router.get("/purchase-orders")
def get_purchase_orders():

    db = SessionLocal()

    try:

        purchase_orders = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                ORDER BY id DESC
            """)
        ).mappings().all()

        return purchase_orders

    finally:
        db.close()

@router.get("/sync/erpnext/purchase-orders")
def sync_erpnext_purchase_orders(
    current_user=Depends(
        get_current_user
    )
):

    return sync_erpnext_purchase_orders_service(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )

@router.post("/push/purchase-orders/erpnext")
def migrate_purchase_orders_to_erpnext(
    current_user=Depends(
        get_current_user
    )
):

    return push_purchase_orders_to_erpnext(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sales-orders")
def get_sales_orders(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()

    try:

        sales_orders = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        return [
            dict(row._mapping)
            for row in sales_orders
        ]

    finally:
        db.close()

@router.get("/sync/erpnext/sales-orders")
def sync_erpnext_sales_orders(
    current_user=Depends(
        get_current_user
    )
):

    return sync_erpnext_sales_orders_service(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )

@router.post("/push/sales-orders/erpnext")
def push_sales_orders_erpnext(
    current_user=Depends(
        get_current_user
    )
):

    return push_sales_orders_to_erpnext(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/accounts")
def get_accounts(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()

    try:

        accounts = db.execute(
            text("""
                SELECT *
                FROM unified_accounts
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        return [
            dict(row._mapping)
            for row in accounts
        ]

    finally:
        db.close()

@router.get("/sync/erpnext/accounts")
def sync_erpnext_accounts(
    current_user=Depends(
        get_current_user
    )
):
    print("ACCOUNTS ROUTE HIT")
    print(sync_erpnext_accounts_service)

    return sync_erpnext_accounts_service(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )