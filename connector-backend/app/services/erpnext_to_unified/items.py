from sqlalchemy import text
from app.database import SessionLocal

from app.services.erpnext_fetch_service import (
    fetch_erpnext_complete_items
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.erpnext_to_unified.transformer import (
    transform_erpnext_item_using_mapping
)


def sync_erpnext_items_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        print("=" * 80)
        print("FETCHING ERPNEXT ITEMS")
        print("=" * 80)

        items = (
            fetch_erpnext_complete_items(
                user_id,
                tenant_id
            )
        )

        print(
            "ITEMS FOUND:",
            len(items)
        )

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

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="erpnext_items",
            source_system="erpnext"
        )

        print("=" * 80)
        print("ERPNEXT → UNIFIED ITEM MAPPING")
        print(mapping)
        print("=" * 80)

        synced = []

        for item in items:

            print()
            print("=" * 80)
            print("RAW ERPNEXT ITEM")
            print(item)
            print("=" * 80)

            transformed_item = (
                transform_erpnext_item_using_mapping(
                    item,
                    mapping
                )
            )

            print()
            print("=" * 80)
            print("TRANSFORMED ITEM")
            print(transformed_item)
            print("=" * 80)

            if not transformed_item.get(
                "item_code"
            ):

                print(
                    "SKIPPED - item_code missing"
                )

                continue

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_items
                    WHERE
                        tenant_id = :tenant_id
                        AND item_code = :item_code
                        AND source = 'erpnext'
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

            print(
                "EXISTING CHECK:",
                transformed_item.get(
                    "item_code"
                ),
                existing
            )

            if existing:

                print(
                    "SKIPPED - ALREADY EXISTS"
                )

                continue

            print()
            print("=" * 80)
            print("INSERTING ITEM")
            print(transformed_item)
            print("=" * 80)

            db.execute(
                text("""
                    INSERT INTO
                    unified_items
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
                        hsn_code,
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
                        :hsn_code,
                        NOW()
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
                        True if transformed_item.get("is_inventory") else False,

                    "is_sold":
                        True if transformed_item.get("is_sold") else False,

                    "is_purchased":
                        True if transformed_item.get("is_purchased") else False,

                    "hsn_code":
                        transformed_item.get(
                            "hsn_code"
                        )
                }
            )

            synced.append(
                transformed_item
            )

        db.commit()

        print()
        print("=" * 80)
        print("SYNC COMPLETE")
        print(
            "TOTAL SYNCED:",
            len(synced)
        )
        print("=" * 80)

        return {

            "message":
                "ERPNext Items synced successfully",

            "total_synced":
                len(synced),

            "items":
                synced
        }

    finally:

        db.close()