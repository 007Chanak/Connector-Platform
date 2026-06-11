from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_item_service import (
    fetch_xero_items
)

from app.transformations.item_transform import (
    transform_xero_item
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def sync_xero_items_service(user_id,tenant_id):

    db = SessionLocal()
    try:

        data = fetch_xero_items(
            user_id, tenant_id
        )

        # Because fetch_xero_items currently returns:
        # {
        #   "status_code": 200,
        #   "response": "....json string...."
        # }
        # we need to handle that.

        if "Items" in data:
            items = data.get(
                "Items",
                []
            )
        else:
            import json

            response_data = json.loads(
                data["response"]
            )

            items = response_data.get(
                "Items",
                []
            )

        synced = []

        for item in items:

            transformed_item = (
                transform_xero_item(item)
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
                    "source": transformed_item["source"]
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
                        unit_price,
                        currency,
                        status,
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
                        :unit_price,
                        :currency,
                        :status,
                        NOW()
                    )
                """),
                {
                    "user_id": user_id,

                    "tenant_id": tenant_id,

                    "source":
                        transformed_item["source"],

                    "external_id":
                        transformed_item["external_id"],

                    "item_code":
                        transformed_item["item_code"],

                    "item_name":
                        transformed_item["item_name"],

                    "description":
                        transformed_item["description"],

                    "unit_price":
                        transformed_item["unit_price"],

                    "currency":
                        transformed_item["currency"],

                    "status":
                        transformed_item["status"]
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