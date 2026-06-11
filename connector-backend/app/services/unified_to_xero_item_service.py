from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_push_service import (
    push_item_to_xero
)

from app.services.sync_log_service import (
    create_sync_log
)
from fastapi import Depends
from app.dependencies.auth import get_current_user



def push_unified_items_to_xero(user_id,tenant_id):

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

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error": "No Xero integration found"
            }

        items = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE
                    tenant_id = :tenant_id
                    AND source != 'xero'
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for item in items:

            result = push_item_to_xero(
                integration.access_token,
                integration.tenant_id,
                item
            )

            create_sync_log(
                user_id=user_id,
                entity_type="item",
                source="unified",
                destination="xero",
                external_id=item.external_id,
                status="success"
            )

            results.append(
                {
                    "item_code":
                        item.item_code,

                    "item_name":
                        item.item_name,

                    "result":
                        result
                }
            )

        return results
    finally:
        db.close()