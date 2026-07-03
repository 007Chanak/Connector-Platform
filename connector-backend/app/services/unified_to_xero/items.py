from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_push_service import (
    push_item_to_xero,
    push_item_exists_check
)

from app.services.mapping_service import (
    get_target_mapping_dict,
    build_payload_from_mapping
)

from app.services.xero_auth_service import (
    refresh_xero_token
)


def push_unified_items_to_xero(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        app_tenant_id = db.execute(
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
                "tenant_id": app_tenant_id
            }
        ).fetchone()

        try:

            refresh_result = refresh_xero_token(
                integration.id
            )

            access_token = refresh_result[
                "access_token"
            ]

        except Exception as e:

            print("=" * 80)
            print("TOKEN REFRESH FAILED")
            print(str(e))
            print("=" * 80)

            access_token = integration.access_token

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        mapping = get_target_mapping_dict(
            app_tenant_id,
            "items",
            "xero"
        )

        print("=" * 80)
        print("ITEM TARGET MAPPING")
        print(mapping)
        print("=" * 80)

        items = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'erpnext'
            """),
            {
                "tenant_id":
                    app_tenant_id
            }
        ).fetchall()

        print("=" * 80)
        print("UNIFIED ITEMS FOUND")
        print(len(items))
        print("=" * 80)

        synced = []

        skipped = []

        for item in items:

            print()
            print("=" * 80)
            print("PROCESSING ITEM")
            print(item.item_code)
            print(item.item_name)
            print("=" * 80)

            migration_check = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :item_code
                """),
                {
                    "tenant_id":
                        app_tenant_id,

                    "item_code":
                        item.item_code
                }
            ).fetchone()

            print(
                "MIGRATION CHECK:",
                migration_check
            )

            if migration_check:

                skipped.append(
                    {
                        "item_code":
                            item.item_code,

                        "reason":
                            "Already Migrated"
                    }
                )

                continue

            exists_in_xero = (
                push_item_exists_check(
                    integration.access_token,
                    integration.tenant_id,
                    item.item_code
                )
            )

            print(
                "XERO EXISTS CHECK:",
                exists_in_xero
            )

            if exists_in_xero:

                skipped.append(
                    {
                        "item_code":
                            item.item_code,

                        "reason":
                            "Already Exists In Xero"
                    }
                )

                continue

            payload = build_payload_from_mapping(
                item,
                mapping
            )

            print("=" * 80)
            print("UNIFIED ITEM")
            print(dict(item._mapping))
            print("=" * 80)

            print("=" * 80)
            print("XERO ITEM PAYLOAD")
            print(payload)
            print("=" * 80)

            response = push_item_to_xero(
                integration.access_token,
                integration.tenant_id,
                payload,
                app_tenant_id
            )

            print("=" * 80)
            print("XERO RESPONSE")
            print(response)
            print("=" * 80)

            success = False

            if isinstance(
                response,
                dict
            ):

                if response.get(
                    "Items"
                ):
                    success = True

            if success:

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
                            app_tenant_id,

                        "user_id":
                            user_id,

                        "source_system":
                            "erpnext",

                        "target_system":
                            "xero",

                        "source_invoice_number":
                            item.item_code
                    }
                )

                db.commit()

            synced.append(
                {
                    "item_code":
                        item.item_code,

                    "item_name":
                        item.item_name,

                    "response":
                        response
                }
            )

        print()
        print("=" * 80)
        print("FINAL RESULTS")
        print(
            {
                "synced":
                    len(synced),

                "skipped":
                    len(skipped)
            }
        )
        print("=" * 80)

        return {

            "message":
                "Items pushed to Xero",

            "total_synced":
                len(synced),

            "total_skipped":
                len(skipped),

            "synced_items":
                synced,

            "skipped_items":
                skipped
        }

    finally:

        db.close()