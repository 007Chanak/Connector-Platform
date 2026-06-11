import requests
from sqlalchemy import text
from app.database import SessionLocal



def fetch_erpnext_items(user_id,tenant_id):

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
            return []

        headers = {
            "Authorization": (
                f"token {erp.api_key}:{erp.api_secret}"
            )
        }

        items_url = (
            f"{erp.erp_url}/api/resource/Item"
        )

        items_response = requests.get(
            items_url,
            headers=headers
        )

        items = items_response.json().get(
            "data",
            []
        )

        complete_items = []

        for item in items:

            item_name = item.get("name")

            item_doc = requests.get(
                f"{erp.erp_url}/api/resource/Item/{item_name}",
                headers=headers
            ).json()["data"]

            complete_items.append(
                item_doc
            )

        return complete_items
    finally:
        db.close()