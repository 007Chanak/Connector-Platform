import requests
from sqlalchemy import text
from decimal import Decimal
from app.database import SessionLocal

from app.services.mapping_service import (
    build_payload_from_mapping,
    get_target_mappings
)


def push_items_to_erpnext(
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

        target_mappings = get_target_mappings(

            tenant_id=tenant_id,

            entity_type="items",

            target_system="erpnext"
        )

        print("=" * 50)
        print("ITEM TARGET MAPPINGS:")
        print(target_mappings)

        items = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchall()

        results = []

        for item in items:

            headers = {

                "Authorization":
                    f"token {erp.api_key}:{erp.api_secret}",

                "Content-Type":
                    "application/json"
            }

            check_url = (
                f"{erp.erp_url}/api/resource/Item/"
                f"{item.item_code}"
            )

            check_response = requests.get(
                check_url,
                headers=headers
            )

            if check_response.status_code == 200:

                results.append(
                    {
                        "item_code":
                            item.item_code,

                        "status":
                            "Skipped - Already Exists"
                    }
                )

                continue

            payload = build_payload_from_mapping(

                item,

                target_mappings.get(
                    "Item",
                    {}
                )
            )
            payload["gst_hsn_code"] = "999799"

            if (
                "item_group"
                not in payload
            ):
                payload[
                    "item_group"
                ] = "Products"

            if (
                "stock_uom"
                not in payload
            ):
                payload[
                    "stock_uom"
                ] = "Nos"

            print("=" * 50)

            print(
                "ITEM CODE:",
                item.item_code
            )

            print(
                "ITEM PAYLOAD:"
            )

            print(
                payload
            )

            for key, value in payload.items():

                if isinstance(value, Decimal):

                    payload[key] = float(value)

            response = requests.post(

                f"{erp.erp_url}/api/resource/Item",

                json=payload,

                headers=headers
            )

            print(
                "ITEM STATUS:"
            )

            print(
                response.status_code
            )

            print(
                "ITEM RESPONSE:"
            )

            print(
                response.text
            )

            try:

                response_json = (
                    response.json()
                )

            except:

                response_json = (
                    response.text
                )

            results.append(
                {
                    "item_code":
                        item.item_code,

                    "status_code":
                        response.status_code,

                    "response":
                        response_json
                }
            )

        return results

    finally:

        db.close()