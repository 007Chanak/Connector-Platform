import requests
from sqlalchemy import text
from app.database import SessionLocal

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.erpnext_fetch_service import (
    fetch_complete_erpnext_sales_orders
)

from app.services.erpnext_to_unified.transformer import (
    transform_erpnext_sales_order_using_mapping,
    transform_erpnext_sales_order_item_using_mapping
)


def sync_erpnext_sales_orders_service(
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

        sales_orders = (
            fetch_complete_erpnext_sales_orders(
                erp.erp_url,
                erp.api_key,
                erp.api_secret
            )
        )

        header_mapping = get_mapping_dict(
            tenant_id,
            "erpnext_sales_orders",
            "erpnext"
        )

        item_mapping = get_mapping_dict(
            tenant_id,
            "erpnext_sales_order_items",
            "erpnext"
        )

        print("=" * 80)
        print("SALES ORDER HEADER MAPPING")
        print(header_mapping)
        print("=" * 80)

        print("=" * 80)
        print("SALES ORDER ITEM MAPPING")
        print(item_mapping)
        print("=" * 80)

        synced_orders = 0
        synced_items = 0

        for so in sales_orders:

            transformed_so = (
                transform_erpnext_sales_order_using_mapping(
                    so,
                    header_mapping
                )
            )

            print("=" * 80)
            print("RAW SALES ORDER")
            print(so)
            print("=" * 80)

            print("=" * 80)
            print("TRANSFORMED SALES ORDER")
            print(transformed_so)
            print("=" * 80)

            existing_so = db.execute(
                text("""
                    SELECT id
                    FROM unified_sales_orders
                    WHERE
                        tenant_id = :tenant_id
                        AND source = 'erpnext'
                        AND external_id = :external_id
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id":
                        transformed_so["external_id"]
                }
            ).fetchone()

            if existing_so:

                print(
                    "SALES ORDER ALREADY EXISTS:",
                    transformed_so["external_id"]
                )

                continue

            if not existing_so:

                db.execute(
                    text("""
                        INSERT INTO
                        unified_sales_orders
                        (
                            tenant_id,
                            user_id,
                            source,
                            external_id,
                            so_number,
                            customer_name,
                            order_date,
                            delivery_date,
                            total_amount,
                            status
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source,
                            :external_id,
                            :so_number,
                            :customer_name,
                            :order_date,
                            :delivery_date,
                            :total_amount,
                            :status
                        )
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "user_id":
                            user_id,

                        "source":
                            "erpnext",

                        "external_id":
                            so.get("name"),

                        "so_number":
                            transformed_so.get(
                                "so_number"
                            ),

                        "customer_name":
                            transformed_so.get(
                                "customer_name"
                            ),

                        "order_date":
                            transformed_so.get(
                                "order_date"
                            ),

                        "delivery_date":
                            transformed_so.get(
                                "delivery_date"
                            ),

                        "total_amount":
                            transformed_so.get(
                                "total_amount"
                            ),

                        "status":
                            transformed_so.get(
                                "status"
                            )
                    }
                )

                synced_orders += 1

            for item in so.get(
                "items",
                []
            ):

                transformed_item = (
                    transform_erpnext_sales_order_item_using_mapping(
                        item,
                        item_mapping
                    )
                )

                existing_item = db.execute(
                    text("""
                        SELECT id
                        FROM unified_sales_order_items
                        WHERE
                            tenant_id = :tenant_id
                            AND so_external_id = :so_external_id
                            AND item_code = :item_code
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "so_external_id":
                            transformed_item.get(
                                "so_external_id"
                            ),

                        "item_code":
                            transformed_item.get(
                                "item_code"
                            )
                    }
                ).fetchone()

                if existing_item:
                    continue

                db.execute(
                    text("""
                        INSERT INTO
                        unified_sales_order_items
                        (
                            tenant_id,
                            user_id,
                            source,
                            so_external_id,
                            item_external_id,
                            item_code,
                            item_name,
                            quantity,
                            unit_price,
                            line_total
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source,
                            :so_external_id,
                            :item_external_id,
                            :item_code,
                            :item_name,
                            :quantity,
                            :unit_price,
                            :line_total
                        )
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "user_id":
                            user_id,

                        "source":
                            "erpnext",

                        "so_external_id":
                            transformed_item.get(
                                "so_external_id"
                            ),

                        "item_external_id":
                            item.get("name"),

                        "item_code":
                            transformed_item.get(
                                "item_code"
                            ),

                        "item_name":
                            transformed_item.get(
                                "item_name"
                            ),

                        "quantity":
                            transformed_item.get(
                                "quantity"
                            ),

                        "unit_price":
                            transformed_item.get(
                                "unit_price"
                            ),

                        "line_total":
                            transformed_item.get(
                                "line_total"
                            )
                    }
                )

                synced_items += 1

        db.commit()

        return {

            "message":
                "Sales Orders synced successfully",

            "sales_orders":
                synced_orders,

            "sales_order_items":
                synced_items
        }

    finally:

        db.close()