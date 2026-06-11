import requests

from sqlalchemy import text

from app.database import SessionLocal

from app.config import (
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET
)


def refresh_xero_token(integration_id):

    db = SessionLocal()
    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id": integration_id
            }
        ).fetchone()

        refresh_token = integration.refresh_token

        token_url = "https://identity.xero.com/connect/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(
            token_url,
            data=data,
            auth=(
                XERO_CLIENT_ID,
                XERO_CLIENT_SECRET
            )
        )

        token_data = response.json()

        new_access_token = token_data["access_token"]
        new_refresh_token = token_data["refresh_token"]

        db.execute(
            text("""
                UPDATE integrations
                SET access_token = :access_token,
                    refresh_token = :refresh_token
                WHERE id = :id
            """),
            {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "id": integration_id
            }
        )

        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
    finally:
        db.close()