import json
import requests

from sqlalchemy import text
from app.database import SessionLocal


def sync_erpnext_accounts_service(
    user_id,
    tenant_id
):
    print("SERVICE STARTED")


    db = SessionLocal()

    try:

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

        print("ERP RECORD:", erp)

        if not erp:

            return {
                "status": "error",
                "message": "ERPNext integration not found"
            }

        response = requests.get(
            f"{erp.erp_url}/api/resource/Account",
            headers={
                "Authorization":
                    f"token {erp.api_key}:{erp.api_secret}"
            },
            params={
                "fields": '["*"]',
                "limit_page_length": 1000
            }
        )
        print("ERP RESPONSE STATUS:", response.status_code)

        if response.status_code != 200:

            return {
                "status": "error",
                "message": response.text
            }

        accounts = response.json().get(
            "data",
            []
        )
        print("TOTAL ACCOUNTS:", len(accounts))

        inserted = 0

        for account in accounts:

            canonical_key = (
                account.get("name")
                or
                account.get("account_name")
            )

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_accounts
                    WHERE
                        tenant_id = :tenant_id
                        AND source = 'erpnext'
                        AND canonical_key = :canonical_key
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "canonical_key":
                        canonical_key
                }
            ).fetchone()

            if existing:
                continue

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
                        parent_account,
                        is_group,
                        company,
                        currency,
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
                        :parent_account,
                        :is_group,
                        :company,
                        :currency,
                        CAST(:raw_data AS JSONB)
                    )
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "source":
                        "erpnext",

                    "account_id":
                        account.get("name"),

                    "canonical_key":
                        canonical_key,

                    "account_code":
                        account.get(
                            "account_number"
                        ),

                    "account_name":
                        account.get(
                            "account_name"
                        ),

                    "account_type":
                        account.get(
                            "account_type"
                        ),

                    "account_class":
                        account.get(
                            "root_type"
                        ),

                    "description":
                        None,

                    "status":
                        "Disabled"
                        if account.get(
                            "disabled"
                        )
                        else "Active",

                    "parent_account":
                        account.get(
                            "parent_account"
                        ),

                    "is_group":
                        bool(
                            account.get(
                                "is_group"
                            )
                        ),

                    "company":
                        account.get(
                            "company"
                        ),

                    "currency":
                        account.get(
                            "account_currency"
                        ),

                    "raw_data":
                        json.dumps(
                            account
                        )
                }
            )

            inserted += 1

        db.commit()

        print("ACCOUNTS SERVICE HIT")

        print(
            "INSERTED:",
            inserted,
            "TOTAL:",
            len(accounts)
        )

        return {
            "status":
                "success",

            "inserted":
                inserted,

            "total_accounts":
                len(accounts)
        }

    finally:

        db.close()