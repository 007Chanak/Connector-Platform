import requests

from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime

from app.database import SessionLocal

from app.services.mapping_service import (
    get_target_mapping_dict,
    build_payload_from_mapping
)


def make_json_safe(obj):

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {
            k: make_json_safe(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            make_json_safe(v)
            for v in obj
        ]

    return obj


def push_invoices_to_erpnext(
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

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not erp:

            return {
                "error":
                    "No ERPNext integration found"
            }

        sales_invoice_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="invoices",
                target_system="erpnext"
            )
        )

        sales_invoice_item_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="invoice_items",
                target_system="erpnext"
            )
        )

        invoices = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE
                    tenant_id = :tenant_id
                    AND origin_system = 'xero'
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchall()

        results = []

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}",
            "Content-Type":
                "application/json"
        }

        for invoice in invoices:

            migration_check = db.execute(
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

            if migration_check:

                results.append(
                    {
                        "invoice_number":
                            invoice.invoice_number,

                        "status":
                            "Skipped - Already Migrated"
                    }
                )

                continue

            customer_check = requests.get(
                f"{erp.erp_url}/api/resource/Customer/{invoice.customer_name}",
                headers=headers
            )

            print("=" * 50)
            print("CUSTOMER RESPONSE")
            print(customer_check.status_code)
            print(customer_check.text)
            print("=" * 50)

            if customer_check.status_code == 200:

                customer_data = customer_check.json().get(
                    "data",
                    {}
                )

                print("=" * 50)
                print("CUSTOMER DATA")
                print(customer_data)
                print("=" * 50)

            if customer_check.status_code != 200:

                results.append(
                    {
                        "invoice_number":
                            invoice.invoice_number,

                        "customer":
                            invoice.customer_name,

                        "status":
                            "Skipped - Customer Not Found"
                    }
                )

                continue

            header_payload = (
                build_payload_from_mapping(
                    invoice,
                    sales_invoice_mapping
                )
            )

            item_rows = db.execute(
                text("""
                    SELECT *
                    FROM unified_invoice_items
                    WHERE
                        tenant_id = :tenant_id
                        AND invoice_external_id = :invoice_external_id
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "invoice_external_id":
                        invoice.external_id
                }
            ).fetchall()

            sales_items = []

            for item_row in item_rows:

                item_payload = (
                    build_payload_from_mapping(
                        item_row,
                        sales_invoice_item_mapping
                    )
                )

                sales_items.append(
                    item_payload
                )

            #
            # ERPNext generates these itself
            #

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
                    (
                        f"Original Xero Invoice: "
                        f"{invoice.invoice_number}"
                    ),

                "items":
                    sales_items,

                "payment_terms_template":
                    None
            }

            payload = make_json_safe(
                payload
            )

            print("=" * 50)
            print("SALES INVOICE PAYLOAD:")
            print(payload)
            print("=" * 50)

            print(
                "POSTING DATE:",
                payload.get("posting_date")
            )

            print(
                "DUE DATE:",
                payload.get("due_date")
            )

            from datetime import datetime

            print(
                "POSTING PARSED:",
                datetime.strptime(
                    str(invoice.invoice_date),
                    "%Y-%m-%d"
                )
            )

            print(
                "DUE PARSED:",
                datetime.strptime(
                    str(invoice.due_date),
                    "%Y-%m-%d"
                )
            )

            print(
                "RAW POSTING:",
                invoice.invoice_date,
                type(invoice.invoice_date)
            )

            print(
                "RAW DUE:",
                invoice.due_date,
                type(invoice.due_date)
            )

            response = requests.post(
                f"{erp.erp_url}/api/resource/Sales Invoice",
                json=payload,
                headers=headers
            )

            print("=" * 50)
            print("SALES INVOICE RESPONSE")
            print(response.status_code)
            print(response.text)
            print("=" * 50)

            if response.status_code in [
                200,
                201
            ]:

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
                        "tenant_id":
                            tenant_id,

                        "user_id":
                            user_id,

                        "source_system":
                            "xero",

                        "target_system":
                            "erpnext",

                        "source_invoice_number":
                            invoice.invoice_number
                    }
                )

                db.commit()

            try:

                response_data = (
                    response.json()
                )

            except Exception:

                response_data = (
                    response.text
                )

            results.append(
                {
                    "invoice_number":
                        invoice.invoice_number,

                    "customer":
                        invoice.customer_name,

                    "status_code":
                        response.status_code,

                    "response":
                        response_data
                }
            )

        return results

    finally:

        db.close()