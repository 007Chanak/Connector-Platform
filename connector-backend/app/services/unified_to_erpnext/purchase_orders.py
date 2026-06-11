import requests
from sqlalchemy import text
from app.database import SessionLocal

def push_purchase_orders_to_erpnext(
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

        purchase_orders = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchall()

        results = []

        processed_pos = set()

        for po in purchase_orders:

            if po.po_number in processed_pos:
                continue

            processed_pos.add(
                po.po_number
            )

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'xero'
                        AND target_system = 'erpnext'
                        AND source_invoice_number = :po_number
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "po_number":
                        po.po_number
                }
            ).fetchone()

            if existing_migration:

                results.append(
                    {
                        "po_number":
                            po.po_number,

                        "status":
                            "Skipped - Already Migrated"
                    }
                )

                continue

            po_rows = db.execute(
                text("""
                    SELECT *
                    FROM unified_purchase_orders
                    WHERE
                        tenant_id = :tenant_id
                        AND po_number = :po_number
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "po_number":
                        po.po_number
                }
            ).fetchall()

            items = []

            for row in po_rows:

                items.append(
                    {
                        "item_code":
                            row.item_code,

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

            payload = {

                "supplier":
                    po.supplier_name,

                "transaction_date":
                    str(po.order_date),

                "schedule_date":
                    str(po.delivery_date),

                "items":
                    items
            }

            headers = {
                "Authorization":
                    f"token {erp.api_key}:{erp.api_secret}",

                "Content-Type":
                    "application/json"
            }

            response = requests.post(
                f"{erp.erp_url}/api/resource/Purchase Order",
                json=payload,
                headers=headers
            )

            try:
                response_json = response.json()
            except Exception:
                response_json = response.text

            print(
                "PO:",
                po.po_number
            )

            print(
                "ERP RESPONSE:",
                response_json
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
                            po.po_number
                    }
                )

                db.commit()

            results.append(
                {
                    "po_number":
                        po.po_number,

                    "status_code":
                        response.status_code,

                    "response":
                        response_json
                }
            )

        return results

    finally:
        db.close()