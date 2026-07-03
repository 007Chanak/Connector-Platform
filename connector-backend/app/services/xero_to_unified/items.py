from sqlalchemy import text

from app.database import SessionLocal

from app.services.mapping_service import (
    get_mapping_dict
)
from app.services.xero_fetch_service import (
    fetch_complete_xero_items
)

from app.services.xero_to_unified.transformer import (
    transform_item_using_mapping
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def sync_xero_items_service(user_id,tenant_id):

    db = SessionLocal()
    try:

        items = fetch_complete_xero_items(
            user_id,
            tenant_id
        )

        synced = []

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="items",
            source_system="xero"
        )

        print("ITEM MAPPING:")
        print(mapping)

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

        for item in items:

            transformed_item = (
                transform_item_using_mapping(
                    item,
                    mapping
                )
            )

            print(
                "ITEM DATA:",
                transformed_item
            )

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_items
                    WHERE
                        tenant_id = :tenant_id
                        AND item_code = :item_code
                        AND source = :source
                """),
                {
                    "tenant_id": tenant_id,
                    "item_code": transformed_item["item_code"],
                    "source": "xero"
                }
            ).fetchone()

            if existing:
                continue

            synced.append(
                transformed_item
            )

            db.execute(
                text("""
                    INSERT INTO unified_items
                    (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        item_code,
                        item_name,
                        description,
                        sales_price,
                        purchase_price,
                        is_inventory,
                        is_sold,
                        is_purchased,
                        created_at
                    )
                    VALUES
                    (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :item_code,
                        :item_name,
                        :description,
                        :sales_price,
                        :purchase_price,
                        :is_inventory,
                        :is_sold,
                        :is_purchased,
                        NOW()
                    )
                """),
                {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "source": "xero",

                    "external_id":
                        transformed_item.get(
                            "external_id"
                        ),

                    "item_code":
                        transformed_item.get(
                            "item_code"
                        ),

                    "item_name":
                        transformed_item.get(
                            "item_name"
                        ),

                    "description":
                        transformed_item.get(
                            "description"
                        ),

                    "sales_price":
                        transformed_item.get(
                            "sales_price"
                        ),

                    "purchase_price":
                        transformed_item.get(
                            "purchase_price"
                        ),

                    "is_inventory":
                        transformed_item.get(
                            "is_inventory"
                        ),

                    "is_sold":
                        transformed_item.get(
                            "is_sold"
                        ),

                    "is_purchased":
                        transformed_item.get(
                            "is_purchased"
                        )
                }
            )

        db.commit()

        return {
            "message":
                "Xero items synced successfully",

            "total_synced":
                len(synced),

            "items":
                synced
        }
    finally:
        db.close()