import json
import requests

from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_auth_service import (
    refresh_xero_token
)


def transform_xero_account(account):

    return {

        "account_id":
            account.get("AccountID"),

        "canonical_key":
            account.get("Code")
            or
            account.get("Name"),

        "account_code":
            account.get("Code"),

        "account_name":
            account.get("Name"),

        "account_type":
            account.get("Type"),

        "account_class":
            account.get("Class"),

        "description":
            account.get("Description"),

        "status":
            account.get("Status"),

        "source":
            "xero",

        "raw_data":
            json.dumps(account)
    }


def sync_xero_accounts_service(
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
                "tenant_id":
                    tenant_id
            }
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/api.xro/2.0/Accounts"
        )

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = refresh_xero_token(
                integration.id
            )

            access_token = (
                refreshed["access_token"]
            )

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        accounts = data.get(
            "Accounts",
            []
        )

        synced = []

        for account in accounts:

            transformed = (
                transform_xero_account(
                    account
                )
            )

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_accounts
                    WHERE
                        tenant_id = :tenant_id
                        AND source = 'xero'
                        AND account_id = :account_id
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "account_id":
                        transformed[
                            "account_id"
                        ]
                }
            ).fetchone()

            if existing:

                db.execute(
                    text("""
                        UPDATE unified_accounts
                        SET
                            canonical_key = :canonical_key,
                            account_code = :account_code,
                            account_name = :account_name,
                            account_type = :account_type,
                            account_class = :account_class,
                            description = :description,
                            status = :status,
                            raw_data = CAST(:raw_data AS JSONB)
                        WHERE id = :id
                    """),
                    {
                        "id":
                            existing.id,

                        "canonical_key":
                            transformed[
                                "canonical_key"
                            ],

                        "account_code":
                            transformed[
                                "account_code"
                            ],

                        "account_name":
                            transformed[
                                "account_name"
                            ],

                        "account_type":
                            transformed[
                                "account_type"
                            ],

                        "account_class":
                            transformed[
                                "account_class"
                            ],

                        "description":
                            transformed[
                                "description"
                            ],

                        "status":
                            transformed[
                                "status"
                            ],

                        "raw_data":
                            transformed[
                                "raw_data"
                            ]
                    }
                )

            else:

                db.execute(
                    text("""
                        INSERT INTO unified_accounts
                        (
                            tenant_id,
                            source,
                            account_id,
                            canonical_key,
                            account_code,
                            account_name,
                            account_type,
                            account_class,
                            description,
                            status,
                            raw_data
                        )
                        VALUES
                        (
                            :tenant_id,
                            :source,
                            :account_id,
                            :canonical_key,
                            :account_code,
                            :account_name,
                            :account_type,
                            :account_class,
                            :description,
                            :status,
                            CAST(:raw_data AS JSONB)
                        )
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "source":
                            transformed[
                                "source"
                            ],

                        "account_id":
                            transformed[
                                "account_id"
                            ],

                        "canonical_key":
                            transformed[
                                "canonical_key"
                            ],

                        "account_code":
                            transformed[
                                "account_code"
                            ],

                        "account_name":
                            transformed[
                                "account_name"
                            ],

                        "account_type":
                            transformed[
                                "account_type"
                            ],

                        "account_class":
                            transformed[
                                "account_class"
                            ],

                        "description":
                            transformed[
                                "description"
                            ],

                        "status":
                            transformed[
                                "status"
                            ],

                        "raw_data":
                            transformed[
                                "raw_data"
                            ]
                    }
                )

            synced.append(
                transformed
            )

        db.commit()

        return {
            "message":
                "Xero Accounts synced successfully",

            "total_synced":
                len(synced),

            "accounts":
                synced
        }

    finally:

        db.close()