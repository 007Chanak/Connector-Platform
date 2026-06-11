from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database import SessionLocal
from app.dependencies.auth import get_current_user
import requests
import json

from app.services.xero_auth_service import (
    refresh_xero_token
)

from app.config import (
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET,
    XERO_REDIRECT_URI
)

router = APIRouter(
    tags=["Integrations"]
)

@router.get("/integrations/status")
def integration_status(
    current_user=Depends(
        get_current_user
    )
):

    db = SessionLocal()
    try:

        xero_connected = db.execute(
            text("""
                SELECT COUNT(*)
                FROM integrations
                WHERE tenant_id_fk = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar() > 0

        erpnext_connected = db.execute(
            text("""
                SELECT COUNT(*)
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": current_user.tenant_id
            }
        ).scalar() > 0

        return {
            "xero_connected":
                xero_connected,

            "erpnext_connected":
                erpnext_connected
        }
    finally:
        db.close()


@router.get("/test/erpnext/accounts")
def test_erpnext_accounts():

    db = SessionLocal()

    try:

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                ORDER BY id DESC
                LIMIT 1
            """)
        ).fetchone()

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        response = requests.get(
            f"{erp.erp_url}/api/resource/Account",
            headers=headers,
            params={
                "fields": '["*"]',
                "limit_page_length": 1000
            }
        )

        print(response.json()["data"][0])

        return response.json()

    finally:
        db.close()

@router.get("/test/xero/accounts")
def test_xero_accounts():

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """)
        ).fetchone()

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Accounts",
            headers={
                "Authorization":
                    f"Bearer {integration.access_token}",

                "Xero-tenant-id":
                    integration.tenant_id,

                "Accept":
                    "application/json"
            }
        )

        return response.json()

    finally:
        db.close()