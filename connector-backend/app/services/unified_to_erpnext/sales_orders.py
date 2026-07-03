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


def push_sales_orders_to_erpnext(
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

        sales_order_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="sales_orders",
                target_system="erpnext"
            )
        )

        sales_order_item_mapping = (
            get_target_mapping_dict(
                tenant_id=tenant_id,
                entity_type="sales_order_items",
                target_system="erpnext"
            )
        )

        print("=" * 80)
        print("SALES ORDER TARGET MAPPING")
        print(sales_order_mapping)
        print("=" * 80)

        print("=" * 80)
        print("SALES ORDER ITEM TARGET MAPPING")
        print(sales_order_item_mapping)
        print("=" * 80)

        sales_orders = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchall()

        print("=" * 80)
        print("SALES ORDERS FOUND")
        print(len(sales_orders))
        print("=" * 80)

        headers = {

            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}",

            "Content-Type":
                "application/json"
        }

        results = []

        for so in sales_orders:

            print("\n")
            print("=" * 80)
            print("PROCESSING SALES ORDER")
            print(so.so_number)
            print("=" * 80)

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'xero'
                        AND target_system = 'erpnext'
                        AND source_invoice_number = :so_number
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "so_number":
                        so.so_number
                }
            ).fetchone()

            print(
                "MIGRATION CHECK:",
                existing_migration
            )

            if existing_migration:

                results.append(
                    {
                        "so_number":
                            so.so_number,

                        "status":
                            "Skipped - Already Migrated"
                    }
                )

                continue

            customer_check = requests.get(
                f"{erp.erp_url}/api/resource/Customer/{so.customer_name}",
                headers=headers
            )

            print(
                "CUSTOMER CHECK:",
                customer_check.status_code
            )

            if customer_check.status_code != 200:

                print(
                    "CUSTOMER NOT FOUND:",
                    so.customer_name
                )

                results.append(
                    {
                        "so_number":
                            so.so_number,

                        "customer":
                            so.customer_name,

                        "status":
                            "Skipped - Customer Not Found"
                    }
                )

                continue

            header_payload = (
                build_payload_from_mapping(
                    so,
                    sales_order_mapping
                )
            )

            print("=" * 80)
            print("HEADER PAYLOAD")
            print(header_payload)
            print("=" * 80)

            item_rows = db.execute(
                text("""
                    SELECT *
                    FROM unified_sales_order_items
                    WHERE
                        tenant_id = :tenant_id
                        AND so_external_id = :so_external_id
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "so_external_id":
                        so.external_id
                }
            ).fetchall()

            print(
                "ITEMS FOUND:",
                len(item_rows)
            )

            sales_items = []

            for item_row in item_rows:

                item_payload = (
                    build_payload_from_mapping(
                        item_row,
                        sales_order_item_mapping
                    )
                )

                print(
                    "ITEM PAYLOAD:",
                    item_payload
                )

                sales_items.append(
                    item_payload
                )

            payload = {

                "customer":
                    so.customer_name,

                "transaction_date":
                    str(
                        so.order_date
                    ),

                "delivery_date":
                    str(
                        so.delivery_date
                    ),

                "items":
                    sales_items
            }

            payload = make_json_safe(
                payload
            )

            print("=" * 80)
            print("FINAL SALES ORDER PAYLOAD")
            print(payload)
            print("=" * 80)

            response = requests.post(
                f"{erp.erp_url}/api/resource/Sales Order",
                json=payload,
                headers=headers
            )

            print("=" * 80)
            print("ERP RESPONSE STATUS")
            print(response.status_code)
            print("=" * 80)

            print("=" * 80)
            print("ERP RESPONSE BODY")
            print(response.text)
            print("=" * 80)

            if response.status_code in [
                200,
                201
            ]:

                print(
                    "MIGRATION SUCCESS"
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
                        "tenant_id":
                            tenant_id,

                        "user_id":
                            user_id,

                        "source_system":
                            "xero",

                        "target_system":
                            "erpnext",

                        "source_invoice_number":
                            so.so_number
                    }
                )

                db.commit()

            else:

                print(
                    "MIGRATION FAILED"
                )

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
                    "so_number":
                        so.so_number,

                    "customer":
                        so.customer_name,

                    "status_code":
                        response.status_code,

                    "response":
                        response_data
                }
            )

        print("\n")
        print("=" * 80)
        print("FINAL RESULTS")
        print(results)
        print("=" * 80)

        return results

    finally:

        db.close()