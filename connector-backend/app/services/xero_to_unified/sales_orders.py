from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_fetch_service import (
    fetch_complete_xero_sales_orders
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.xero_to_unified.transformer import (
    transform_sales_order_using_mapping,
    transform_sales_order_item_using_mapping
)


def sync_xero_sales_orders_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        sales_orders = (
            fetch_complete_xero_sales_orders(
                user_id,
                tenant_id
            )
        )

        sales_order_mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="sales_orders",
            source_system="xero"
        )

        sales_order_item_mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="sales_order_items",
            source_system="xero"
        )

        synced = []

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

        valid_statuses = [
            "DRAFT",
            "SENT",
            "ACCEPTED",
            "INVOICED"
        ]

        for sales_order in sales_orders:

            if sales_order.get(
                "Status"
            ) not in valid_statuses:
                continue

            transformed_so = (
                transform_sales_order_using_mapping(
                    sales_order,
                    sales_order_mapping
                )
            )

            print("=" * 80)
            print("SALES ORDER")
            print(transformed_so)
            print("=" * 80)

            existing_so = db.execute(
                text("""
                    SELECT id
                    FROM unified_sales_orders
                    WHERE
                        tenant_id = :tenant_id
                        AND external_id = :external_id
                        AND source = 'xero'
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id":
                        transformed_so[
                            "external_id"
                        ]
                }
            ).fetchone()

            if existing_so:
                continue

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
                        status,
                        canonical_key,
                        created_at
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
                        :status,
                        :canonical_key,
                        NOW()
                    )
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "user_id":
                        user_id,

                    "source":
                        "xero",

                    "external_id":
                        transformed_so.get(
                            "external_id"
                        ),

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
                        ),

                    "canonical_key":
                        transformed_so.get(
                            "so_number"
                        )
                }
            )

            for line_item in sales_order.get(
                "LineItems",
                []
            ):

                transformed_item = (
                    transform_sales_order_item_using_mapping(
                        line_item,
                        sales_order_item_mapping
                    )
                )

                print(
                    "SALES ORDER ITEM:"
                )

                print(
                    transformed_item
                )

                item_name = transformed_item.get(
                    "item_name"
                )

                if not item_name:

                    item_row = db.execute(
                        text("""
                            SELECT item_name
                            FROM unified_items
                            WHERE
                                tenant_id = :tenant_id
                                AND item_code = :item_code
                            LIMIT 1
                        """),
                        {
                            "tenant_id":
                                tenant_id,

                            "item_code":
                                transformed_item.get(
                                    "item_code"
                                )
                        }
                    ).fetchone()

                    item_name = (
                        item_row.item_name
                        if item_row
                        else None
                    )

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
                            "xero",

                        "so_external_id":
                            transformed_so.get(
                                "external_id"
                            ),

                        "item_external_id":
                            transformed_item.get(
                                "item_external_id"
                            ),

                        "item_code":
                            transformed_item.get(
                                "item_code"
                            ),

                        "item_name":
                            item_name,

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

            synced.append(
                transformed_so
            )

        db.commit()

        return {

            "message":
                "Sales Orders synced successfully",

            "total_synced":
                len(synced),

            "sales_orders":
                synced
        }

    finally:

        db.close()