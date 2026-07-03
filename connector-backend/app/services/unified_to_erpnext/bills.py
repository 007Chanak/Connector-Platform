import requests
from collections import defaultdict
from sqlalchemy import text

from app.database import SessionLocal

from app.services.mapping_service import (
    get_target_mapping_dict,
    build_payload_from_mapping
)

from decimal import Decimal
from datetime import date, datetime


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

def push_bills_to_erpnext(
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

        purchase_invoice_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="bills",
                target_system="erpnext",
                target_doctype="Purchase Invoice"
            )
        )

        purchase_invoice_item_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="bill_items",
                target_system="erpnext",
                target_doctype="Purchase Invoice Item"
            )
        )

        bills = db.execute(
            text("""
                SELECT *
                FROM unified_bills
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
                ORDER BY bill_number
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

        for bill in bills:

            migration_check = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'xero'
                        AND target_system = 'erpnext'
                        AND source_invoice_number = :bill_number
                """),
                {
                    "tenant_id": tenant_id,
                    "bill_number": bill.bill_number
                }
            ).fetchone()

            if migration_check:

                results.append(
                    {
                        "bill_number":
                            bill.bill_number,
                        "status":
                            "Skipped - Already Migrated"
                    }
                )

                continue

            supplier_check = requests.get(
                f"{erp.erp_url}/api/resource/Supplier/{bill.supplier_name}",
                headers=headers
            )

            if supplier_check.status_code != 200:

                results.append(
                    {
                        "bill_number":
                            bill.bill_number,

                        "supplier":
                            bill.supplier_name,

                        "status":
                            "Skipped - Supplier Not Found"
                    }
                )

                continue

            header_payload = (
                build_payload_from_mapping(
                    bill,
                    purchase_invoice_mapping
                )
            )

            item_rows = db.execute(
                text("""
                    SELECT *
                    FROM unified_bill_items
                    WHERE
                        tenant_id = :tenant_id
                        AND bill_external_id = :bill_external_id
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "bill_external_id":
                        bill.external_id
                }
            ).fetchall()

            purchase_items = []

            for item_row in item_rows:

                item_payload = (
                    build_payload_from_mapping(
                        item_row,
                        purchase_invoice_item_mapping
                    )
                )

                purchase_items.append(
                    item_payload
                )

            header_payload["items"] = (
                purchase_items
            )

            header_payload.pop("status",None)

            header_payload = make_json_safe(header_payload)

            print("=" * 50)
            print("PURCHASE INVOICE PAYLOAD:")
            print(header_payload)
            print("=" * 50)

            response = requests.post(
                f"{erp.erp_url}/api/resource/Purchase Invoice",
                json=header_payload,
                headers=headers
            )

            print("=" * 50)
            print("PURCHASE INVOICE RESPONSE")
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
                            bill.bill_number
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
                    "bill_number":
                        bill.bill_number,

                    "supplier":
                        bill.supplier_name,

                    "status_code":
                        response.status_code,

                    "response":
                        response_data
                }
            )

        return results

    finally:

        db.close()