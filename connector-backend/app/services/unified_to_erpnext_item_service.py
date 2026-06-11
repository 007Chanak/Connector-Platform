import requests
from sqlalchemy import text
from app.database import SessionLocal
from fastapi import Depends
from app.dependencies.auth import get_current_user



def push_items_to_erpnext(user_id,tenant_id):

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
                "tenant_id": tenant_id,
            }
        ).fetchone()

        if not erp:
            return {
                "error": "No ERPNext integration found"
            }

        items = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for item in items:

            headers = {
                "Authorization": (
                    f"token {erp.api_key}:{erp.api_secret}"
                ),
                "Content-Type": "application/json"
            }

            # Duplicate check
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

            url = (
                f"{erp.erp_url}/api/resource/Item"
            )

            payload = {
                "item_code": item.item_code,

                "item_name": item.item_name,

                "item_group": "Products",

                "stock_uom": "Nos",

                "gst_hsn_code": "010129"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers
            )

            results.append(
                {
                    "item_code":
                        item.item_code,

                    "status_code":
                        response.status_code,

                    "response":
                        response.json()
                }
            )

        return results
    finally:
        db.close()