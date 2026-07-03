from fastapi import APIRouter
import requests
from sqlalchemy import text
from app.database import engine
from app.database import SessionLocal
import json

from fastapi import Depends
from app.dependencies.auth import get_current_user

from app.transformations.customer_transform import (
    transform_xero_contact
)
from app.services.xero_invoice_service import (
    fetch_xero_invoices
)

from app.services.xero_item_service import (
    fetch_xero_items
)

from app.config import (
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET,
    XERO_REDIRECT_URI
)

from app.services.xero_to_unified.customers import (
    sync_xero_customers_service
)

from app.services.xero_to_unified.invoices import (
    sync_xero_invoices_service
)

from app.services.unified_to_xero_invoice_service import (
    push_unified_invoices_to_xero
)

from app.services.xero_to_unified.items import (
    sync_xero_items_service
)

from app.services.unified_to_xero.items import (
    push_unified_items_to_xero
)

from app.services.unified_to_xero.customers import (
    push_unified_customers_to_xero
)

from app.services.xero_auth_service import (
    refresh_xero_token
)

from app.services.xero_to_unified.suppliers import (
    sync_xero_suppliers_service
)

from app.services.unified_to_xero.suppliers import (
    push_unified_suppliers_to_xero
)

from app.services.xero_to_unified.bills import (
    sync_xero_bills_service
)

from app.services.unified_to_xero.bills import (
    push_unified_bills_to_xero
)

from app.services.xero_to_unified.purchase_orders import (
    sync_xero_purchase_orders_service
)

from app.services.unified_to_xero.purchase_orders import (
    push_unified_purchase_orders_to_xero
)

from app.services.xero_to_unified.sales_orders import (
    sync_xero_sales_orders_service
)

from app.services.unified_to_xero.sales_orders import (
    push_unified_sales_orders_to_xero
)

from app.services.xero_to_unified.accounts import (
    sync_xero_accounts_service
)
 
router = APIRouter()


@router.get("/xero/login")
def xero_login(
    current_user=Depends(get_current_user)
):

    auth_url = (
        f"https://login.xero.com/identity/connect/authorize?"
        f"response_type=code"
        f"&client_id={XERO_CLIENT_ID}"
        f"&redirect_uri={XERO_REDIRECT_URI}"
        f"&scope=openid profile email "
        "accounting.contacts "
        "accounting.invoices "
        "accounting.settings "
        "accounting.settings.read "
        "offline_access"
        f"&state={current_user.id}"
    )

    return {
        "auth_url": auth_url
    }


@router.get("/callback")
def callback(code: str, state: str):

    db = SessionLocal()
    try:
        user_id = int(state)


        app_tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).scalar()

        token_url = "https://identity.xero.com/connect/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": XERO_REDIRECT_URI
        }

        response = requests.post(
            token_url,
            data=data,
            auth=(
                XERO_CLIENT_ID,
                XERO_CLIENT_SECRET
            )
        )

        token_data = response.json()

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]

        # Get Xero tenant details
        connections_response = requests.get(
            "https://api.xero.com/connections",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        connections = connections_response.json()

        tenant_id = connections[0]["tenantId"]

        # Save integration
        db.execute(
            text("""
                INSERT INTO integrations
                (
                    user_id,
                    provider,
                    access_token,
                    refresh_token,
                    tenant_id,
                    tenant_id_fk
                )
                VALUES
                (
                    :user_id,
                    :provider,
                    :access_token,
                    :refresh_token,
                    :tenant_id,
                    :tenant_id_fk
                )
            """),
            {
                "user_id": user_id,
                "provider": "xero",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "tenant_id": tenant_id,
                "tenant_id_fk": app_tenant_id
            }
        )

        db.commit()

        return {
            "message": "Xero connected successfully",
            "tenant_id": tenant_id
        }
    finally:
        db.close()


@router.get("/xero/contacts")
def get_contacts(
    access_token: str,
    tenant_id: str
):

    url = "https://api.xero.com/api.xro/2.0/Contacts"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    query = text("""
        INSERT INTO raw_xero_contacts
        (
            tenant_id,
            raw_json
        )
        VALUES
        (
            :tenant_id,
            :raw_json
        )
    """)

    with engine.connect() as conn:

        conn.execute(
            query,
            {
                "tenant_id": tenant_id,
                "raw_json": json.dumps(data)
            }
        )

        conn.commit()

    return data


@router.get("/xero/connections")
def get_connections(access_token: str):

    url = "https://api.xero.com/connections"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    return response.json()


@router.get("/xero/transformed-contacts")
def transformed_contacts(
    access_token: str,
    tenant_id: str,
    current_user=Depends(get_current_user)
):

    db = SessionLocal()
    try:

        url = "https://api.xero.com/api.xro/2.0/Contacts"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": tenant_id,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)

        data = response.json()

        contacts = data.get("Contacts", [])

        transformed = []

        for contact in contacts:

            customer = transform_xero_contact(contact)

            transformed.append(customer)

            db.execute(
                text("""
                    INSERT INTO unified_customers (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        customer_name,
                        email,
                        phone,
                        address,
                        postal_code,
                        tax_number,
                        website,
                        status,
                        created_at
                    )
                    VALUES (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :customer_name,
                        :email,
                        :phone,
                        :address,
                        :postal_code,
                        :tax_number,
                        :website,
                        :status,
                        :created_at
                    )
                """),
                {
                    "user_id": current_user.id,   # current_user.id in xero_routes

                    "tenant_id": tenant_id,

                    "source": customer.get("source"),

                    "external_id": customer.get("external_id"),

                    "customer_name": customer.get("customer_name"),

                    "email": customer.get("email"),

                    "phone": customer.get("phone"),

                    "address": customer.get("address"),

                    "postal_code": customer.get("postal_code"),

                    "tax_number": customer.get("tax_number"),

                    "website": customer.get("website"),

                    "status": customer.get("status"),

                    "created_at": customer.get("created_at")
                }
            )

        db.commit()

        return transformed
    finally:
        db.close()


@router.get("/sync/xero/customers")
def sync_xero_customers(
    current_user=Depends(get_current_user)
):

    return sync_xero_customers_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/xero/invoices")
def get_xero_invoices(
    current_user=Depends(get_current_user)
):

    return fetch_xero_invoices(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/xero/invoices")
def sync_xero_invoices(
    current_user=Depends(
        get_current_user
    )
):

    return sync_xero_invoices_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/invoices/xero")
def sync_invoices_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": current_user.tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error":
                    "No Xero integration found"
            }

        return push_unified_invoices_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id,
            integration.id
        )
    finally:
        db.close()

@router.get("/xero/items")
def get_xero_items(
    current_user=Depends(
        get_current_user
    )
):

    return fetch_xero_items(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/xero/items")
def sync_xero_items(
    current_user=Depends(
        get_current_user
    )
):

    return sync_xero_items_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/items/xero")
def sync_items_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    return push_unified_items_to_xero(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/sync/customers/xero")
def sync_customers_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": current_user.tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error":
                    "No Xero integration found"
            }

        refreshed = refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id": integration.id
            }
        ).fetchone()

        return push_unified_customers_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id
        )
    finally:
        db.close()


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
            {
                "user_id": current_user.id
            }
        ).scalar()

        suppliers = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
            """),
            {
                "tenant_id": tenant_id
            }
        ).mappings().all()

        return suppliers

    finally:
        db.close()


@router.get("/sync/xero/suppliers")
def sync_xero_suppliers(
    current_user=Depends(get_current_user)
):
    return sync_xero_suppliers_service(
        current_user.id,
        None
    )

@router.get("/push/suppliers/xero")
def push_suppliers_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": current_user.tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error":
                    "No Xero integration found"
            }

        refreshed = refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id": integration.id
            }
        ).fetchone()

        return push_unified_suppliers_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id
        )

    finally:
        db.close()

@router.get("/sync/xero/bills")
def sync_xero_bills(
    current_user=Depends(get_current_user)
):
    return sync_xero_bills_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/push/bills/xero")
def push_bills_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": current_user.tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id": integration.id
            }
        ).fetchone()

        return push_unified_bills_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id,
            integration.id
        )

    finally:
        db.close()

@router.get("/test/xero/purchase-orders")
def test_xero_purchase_orders():

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """)
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/PurchaseOrders",
            headers={
                "Authorization":
                    f"Bearer {integration.access_token}",

                "Xero-tenant-id":
                    integration.tenant_id,

                "Accept":
                    "application/json"
            }
        )

        data = response.json()

        print(
            json.dumps(
                data,
                indent=4
            )
        )

        return data

    finally:
        db.close()

@router.get("/sync/xero/purchase-orders")
def sync_xero_purchase_orders(
    current_user=Depends(
        get_current_user
    )
):

    return sync_xero_purchase_orders_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/push/purchase-orders/xero")
def push_purchase_orders_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id,
            }
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        return push_unified_purchase_orders_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id,
            integration.id
        )

    finally:
        db.close()

@router.get("/test/xero/quotes")
def test_xero_quotes():

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """)
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Quotes",
            headers={
                "Authorization":
                    f"Bearer {integration.access_token}",

                "Xero-tenant-id":
                    integration.tenant_id,

                "Accept":
                    "application/json"
            }
        )

        data = response.json()

        print(
            json.dumps(
                data,
                indent=4
            )
        )

        return data

    finally:
        db.close()

@router.get("/sync/xero/sales-orders")
def sync_xero_sales_orders(
    current_user=Depends(
        get_current_user
    )
):

    return sync_xero_sales_orders_service(
        current_user.id,
        current_user.tenant_id
    )

@router.get("/push/sales-orders/xero")
def push_sales_orders_to_xero(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id,
            }
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        return push_unified_sales_orders_to_xero(
            integration.access_token,
            integration.tenant_id,
            current_user.id,
            integration.id
        )

    finally:
        db.close()

@router.get("/sync/xero/accounts")
def sync_xero_accounts(
    current_user=Depends(
        get_current_user
    )
):

    return sync_xero_accounts_service(
        current_user.id,
        current_user.tenant_id
    )