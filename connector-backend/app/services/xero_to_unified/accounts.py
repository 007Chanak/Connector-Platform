import json
import requests

from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_fetch_service import (
    fetch_complete_xero_accounts
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.xero_to_unified.transformer import (
    transform_account_using_mapping
)

def sync_xero_accounts_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        accounts = (
            fetch_complete_xero_accounts(
                user_id,
                tenant_id
            )
        )

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="accounts",
            source_system="xero"
        )

        synced = []

        for account in accounts:

            transformed_account = (
                transform_account_using_mapping(
                    account,
                    mapping
                )
            )

            existing_account = db.execute(
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
                        transformed_account[
                            "account_id"
                        ]
                }
            ).fetchone()

            if existing_account:
                continue

            db.execute(
                text("""
                    INSERT INTO unified_accounts
                    (
                        tenant_id,
                        source,
                        account_id,
                        account_code,
                        account_name,
                        account_type,
                        account_class,
                        description,
                        status,
                        canonical_key,
                        raw_data,
                        created_at
                    )
                    VALUES
                    (
                        :tenant_id,
                        :source,
                        :account_id,
                        :account_code,
                        :account_name,
                        :account_type,
                        :account_class,
                        :description,
                        :status,
                        :canonical_key,
                        CAST(:raw_data AS jsonb),
                        NOW()
                    )
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "source":
                        "xero",

                    "account_id":
                        transformed_account.get(
                            "account_id"
                        ),

                    "account_code":
                        transformed_account.get(
                            "account_code"
                        ),

                    "account_name":
                        transformed_account.get(
                            "account_name"
                        ),

                    "account_type":
                        transformed_account.get(
                            "account_type"
                        ),

                    "account_class":
                        transformed_account.get(
                            "account_class"
                        ),

                    "description":
                        transformed_account.get(
                            "description"
                        ),

                    "status":
                        transformed_account.get(
                            "status"
                        ),

                    "canonical_key":
                        transformed_account.get(
                            "account_code"
                        ),

                    "raw_data":
                        json.dumps(
                            account
                        )
                }
            )

            synced.append(
                transformed_account
            )

        db.commit()

        return {
            "message":
                "Accounts synced successfully",

            "total_synced":
                len(synced),

            "accounts":
                synced
        }

    finally:

        db.close()