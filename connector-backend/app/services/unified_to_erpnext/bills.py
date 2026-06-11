import requests
from collections import defaultdict
from sqlalchemy import text

from app.database import SessionLocal


def push_bills_to_erpnext(user_id, tenant_id):

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
                "error": "No ERPNext integration found"
            }

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

        grouped_bills = defaultdict(list)

        for bill in bills:
            grouped_bills[bill.bill_number].append(bill)

        results = []

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}",
            "Content-Type":
                "application/json"
        }

        for bill_number, bill_rows in grouped_bills.items():

            first_bill = bill_rows[0]

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
                    "bill_number": bill_number
                }
            ).fetchone()

            if migration_check:

                results.append(
                    {
                        "bill_number": bill_number,
                        "status": "Skipped - Already Migrated"
                    }
                )

                continue

            supplier_check = requests.get(
                f"{erp.erp_url}/api/resource/Supplier/{first_bill.supplier_name}",
                headers=headers
            )

            if supplier_check.status_code != 200:

                results.append(
                    {
                        "bill_number": bill_number,
                        "supplier": first_bill.supplier_name,
                        "status": "Skipped - Supplier Not Found"
                    }
                )

                continue

            purchase_items = []

            for row in bill_rows:

                purchase_items.append(
                    {
                        "item_code":
                            row.item_code
                            if row.item_code
                            else "TEST-001",

                        "qty":
                            float(row.quantity)
                            if row.quantity
                            else 1,

                        "rate":
                            float(row.unit_price)
                            if row.unit_price
                            else 0
                    }
                )

            if not purchase_items:

                purchase_items = [
                    {
                        "item_code": "TEST-001",
                        "qty": 1,
                        "rate":
                            float(first_bill.total_amount)
                            if first_bill.total_amount
                            else 0
                    }
                ]

            payload = {
                "supplier":
                    first_bill.supplier_name,

                "bill_no":
                    first_bill.bill_number,

                "set_posting_time":
                    1,

                "posting_date":
                    str(first_bill.bill_date),

                "due_date":
                    str(first_bill.due_date),

                "remarks":
                    f"Original Xero Bill: {first_bill.bill_number}",

                "items":
                    purchase_items
            }

            response = requests.post(
                f"{erp.erp_url}/api/resource/Purchase Invoice",
                json=payload,
                headers=headers
            )

            if response.status_code in [200, 201]:

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
                            bill_number
                    }
                )

                db.commit()

            try:
                response_data = response.json()
            except Exception:
                response_data = response.text

            results.append(
                {
                    "bill_number":
                        bill_number,

                    "supplier":
                        first_bill.supplier_name,

                    "status_code":
                        response.status_code,

                    "response":
                        response_data
                }
            )

        return results

    finally:
        db.close()