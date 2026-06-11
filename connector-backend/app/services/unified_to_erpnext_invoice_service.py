import requests

from sqlalchemy import text

from app.database import SessionLocal
from fastapi import Depends
from app.dependencies.auth import get_current_user


def push_unified_invoices_to_erpnext(user_id,tenant_id):

    db = SessionLocal()
    try:

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

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchone()

        if not erp:
            return {
                "error": "No ERPNext integration found"
            }

        invoices = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE
                    tenant_id = :tenant_id
                    AND origin_system = 'xero'
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for invoice in invoices:

            headers = {
                "Authorization": (
                    f"token {erp.api_key}:{erp.api_secret}"
                ),
                "Content-Type": "application/json"
            }

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'xero'
                        AND target_system = 'erpnext'
                        AND source_invoice_number = :invoice_number
                """),
                {
                    "tenant_id": tenant_id,
                    "invoice_number":
                        invoice.invoice_number
                }
            ).fetchone()

            print(
                "CHECKING:",
                invoice.invoice_number,
                existing_migration
            )

            if existing_migration:

                results.append(
                    {
                        "invoice_number":
                            invoice.invoice_number,

                        "status":
                            "Skipped - Already Migrated"
                    }
                )

                continue

            url = (
                f"{erp.erp_url}/api/resource/Sales Invoice"
            )

            invoice_items = db.execute(
                text("""
                    SELECT *
                    FROM unified_invoice_items
                    WHERE
                        tenant_id = :tenant_id
                        AND invoice_external_id = :external_id
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id": invoice.external_id
                }
            ).fetchall()

            erp_items = []

            for item in invoice_items:

                erp_items.append(
                    {
                        "item_code":
                            item.item_code
                            if item.item_code
                            else "TEST-001",

                        "qty":
                            float(item.quantity)
                            if item.quantity
                            else 1,

                        "rate":
                            float(item.unit_price)
                            if item.unit_price
                            else 0
                    }
                )
            
            if not erp_items:
                erp_items = [
                    {
                        "item_code": "TEST-001",
                        "qty": 1,
                        "rate": float(invoice.total_amount)
                    }
                ]

            payload = {
                "customer":
                    invoice.customer_name,

                "set_posting_time":
                    1,

                "posting_date":
                    str(invoice.invoice_date),

                "due_date":
                    str(invoice.due_date),

                "remarks":
                    f"Original Xero Invoice: {invoice.invoice_number}",

                "items": erp_items
            }

            print(
                "INVOICE:",
                invoice.invoice_number
            )

            print(
                "POSTING DATE:",
                invoice.invoice_date
            )

            print(
                "DUE DATE:",
                invoice.due_date
            )

            response = requests.post(
                url,
                json=payload,
                headers=headers
            )

            if response.status_code in [200, 201]:

                erp_invoice_id = (
                    response.json()
                    .get("data", {})
                    .get("name")
                )

                db.execute(
                    text("""
                        INSERT INTO migration_logs
                        (
                            tenant_id,
                            user_id,
                            source_system,
                            target_system,
                            source_invoice_number
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source_system,
                            :target_system,
                            :source_invoice_number
                        )
                    """),
                    {
                        "user_id":
                            user_id,

                        "tenant_id": app_tenant_id,

                        "source_system":
                            "xero",

                        "target_system":
                            "erpnext",

                        "source_invoice_number":
                            invoice.invoice_number
                    }
                )

                db.commit()

            results.append(
                {
                    "invoice_number":
                        invoice.invoice_number,

                    "status_code":
                        response.status_code,

                    "response":
                        response.json()
                }
            )

        return results
    finally:
        db.close()