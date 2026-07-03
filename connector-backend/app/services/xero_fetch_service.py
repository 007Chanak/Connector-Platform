import requests
from sqlalchemy import text
from app.database import SessionLocal
from app.services.xero_auth_service import (
    refresh_xero_token
)


def fetch_complete_xero_customers(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:

            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Contacts"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        contacts = data.get(
            "Contacts",
            []
        )

        return contacts

    finally:

        db.close()

def fetch_complete_xero_suppliers(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:

            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Contacts"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        contacts = data.get(
            "Contacts",
            []
        )

        suppliers = []

        for contact in contacts:
            print(
                contact.get("Name"),
                contact.get("IsSupplier")
            )

            if contact.get(
                "IsSupplier"
            ):

                suppliers.append(
                    contact
                )

        return suppliers

    finally:

        db.close()


def fetch_complete_xero_items(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:
            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Items"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        return data.get(
            "Items",
            []
        )

    finally:

        db.close()


def fetch_complete_xero_items(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:

            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Items"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        return data.get(
            "Items",
            []
        )

    finally:

        db.close()

def fetch_complete_xero_invoices(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:

            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Invoices"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        invoices = data.get(
            "Invoices",
            []
        )

        complete_invoices = []

        valid_statuses = [
            "DRAFT",
            "AUTHORISED",
            "PAID",
            "UNPAID"
        ]

        for invoice in invoices:

            if invoice.get(
                "Type"
            ) != "ACCREC":
                continue

            if invoice.get(
                "Status"
            ) not in valid_statuses:
                continue

            invoice_id = invoice.get(
                "InvoiceID"
            )

            detail_url = (
                f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}"
            )

            detail_response = requests.get(
                detail_url,
                headers=headers
            )

            detail_data = (
                detail_response.json()
            )

            detailed_invoice = (
                detail_data.get(
                    "Invoices",
                    [{}]
                )[0]
            )

            print(
                "DETAIL INVOICE:",
                detailed_invoice.get(
                    "InvoiceNumber"
                )
            )

            print(
                "LINE ITEMS:",
                len(
                    detailed_invoice.get(
                        "LineItems",
                        []
                    )
                )
            )

            print(
                "FETCHED:",
                detailed_invoice.get("Type"),
                detailed_invoice.get("InvoiceNumber"),
                detailed_invoice.get("Contact", {}).get("Name")
            )

            complete_invoices.append(
                detailed_invoice
            )

        return complete_invoices

    finally:

        db.close()


def fetch_complete_xero_bills(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:

            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Invoices"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        invoices = data.get(
            "Invoices",
            []
        )

        complete_bills = []

        seen = set()

        valid_statuses = [
            "DRAFT",
            "AUTHORISED",
            "PAID",
            "UNPAID"
        ]

        for invoice in invoices:

            if invoice.get(
                "Type"
            ) != "ACCPAY":
                continue

            if invoice.get(
                "Status"
            ) not in valid_statuses:
                continue

            bill_number = invoice.get(
                "InvoiceNumber"
            )

            if bill_number in seen:
                continue

            seen.add(
                bill_number
            )

            invoice_id = invoice.get(
                "InvoiceID"
            )

            detail_url = (
                f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}"
            )

            detail_response = requests.get(
                detail_url,
                headers=headers
            )

            detail_data = (
                detail_response.json()
            )

            detailed_bill = (
                detail_data.get(
                    "Invoices",
                    [{}]
                )[0]
            )

            complete_bills.append(
                detailed_bill
            )

        return complete_bills

    finally:

        db.close()

from sqlalchemy import text
import requests

from app.database import SessionLocal

from app.services.xero_auth_service import (
    refresh_xero_token
)


def fetch_complete_xero_sales_orders(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:
            return []

        headers = {

            "Authorization":
                f"Bearer {integration.access_token}",

            "Xero-tenant-id":
                integration.tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Quotes",
            headers=headers
        )

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            headers["Authorization"] = (
                f"Bearer {refreshed['access_token']}"
            )

            response = requests.get(
                "https://api.xero.com/api.xro/2.0/Quotes",
                headers=headers
            )

        quotes = response.json().get(
            "Quotes",
            []
        )

        sales_orders = []

        valid_statuses = [
            "DRAFT",
            "SENT",
            "ACCEPTED",
            "INVOICED"
        ]

        for quote in quotes:

            if quote.get(
                "Status"
            ) not in valid_statuses:
                continue

            sales_orders.append(
                quote
            )

        return sales_orders

    finally:

        db.close()

def fetch_complete_xero_purchase_orders(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:
            return []

        access_token = integration.access_token
        xero_tenant_id = integration.tenant_id

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/PurchaseOrders",
            headers=headers
        )

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = refreshed[
                "access_token"
            ]

            headers[
                "Authorization"
            ] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                "https://api.xero.com/api.xro/2.0/PurchaseOrders",
                headers=headers
            )

        purchase_orders = (
            response.json().get(
                "PurchaseOrders",
                []
            )
        )

        complete_purchase_orders = []

        for po in purchase_orders:
            if po.get("Status") == "DELETED":
                continue

            complete_purchase_orders.append(
                po
            )

        return complete_purchase_orders

    finally:
        db.close()

def fetch_complete_xero_accounts(
    user_id,
    tenant_id
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
                "user_id": user_id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not integration:
            return []

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Accounts",
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                "https://api.xero.com/api.xro/2.0/Accounts",
                headers=headers
            )

            data = response.json()

        return data.get(
            "Accounts",
            []
        )

    finally:

        db.close()