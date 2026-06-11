import requests
from sqlalchemy import text

from app.database import SessionLocal
from app.services.xero_auth_service import (
    refresh_xero_token
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def fetch_xero_items(user_id,tenant_id):

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

        access_token = integration.access_token
        xero_tenant_id = integration.tenant_id

        url = "https://api.xero.com/api.xro/2.0/Items"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": xero_tenant_id,
            "Accept": "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = refreshed[
                "access_token"
            ]

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        return {
            "status_code": response.status_code,
            "response": response.text
        }
    finally:
        db.close()