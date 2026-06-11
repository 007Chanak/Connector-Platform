from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_push_service import (
    push_invoice_to_xero,
    invoice_exists_in_xero
)

from app.services.xero_auth_service import (
    refresh_xero_token
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def push_unified_invoices_to_xero(
    access_token,
    tenant_id,
    user_id,
    integration_id
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

        invoices = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE
                    tenant_id = :tenant_id
                    AND origin_system = 'erpnext'
            """),
            {
                "tenant_id": app_tenant_id,
            }
        ).fetchall()

        results = []

        for invoice in invoices:

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :invoice_number
                """),
                {
                    "tenant_id": app_tenant_id,
                    "invoice_number":
                        invoice.invoice_number
                }
            ).fetchone()

            print(
                "CHECKING:",
                invoice.invoice_number,
                existing_migration
            )

            if existing_migration:

                print(
                    "MIGRATION LOG FOUND FOR:",
                    invoice.invoice_number
                )

                exists_in_xero = invoice_exists_in_xero(
                    access_token,
                    tenant_id,
                    invoice.invoice_number
                )

                print(
                    "EXISTS IN XERO:",
                    exists_in_xero
                )

                if exists_in_xero:

                    print(
                        "SKIPPING:",
                        invoice.invoice_number
                    )

                    results.append(
                        {
                            "invoice_number":
                                invoice.invoice_number,

                            "status":
                                "Skipped - Already Migrated"
                        }
                    )

                    continue

                print(
                    "RECREATING:",
                    invoice.invoice_number
                )

            response = push_invoice_to_xero(
                access_token,
                tenant_id,
                invoice
            )

            print("INVOICE:", invoice.invoice_number)
            print("STATUS:", response["status_code"])
            print("RESPONSE:", response["response"])


            if response["status_code"] in [200, 201]:

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
                        "user_id":
                            user_id,
                        
                        "tenant_id": app_tenant_id,

                        "source_system":
                            "erpnext",

                        "target_system":
                            "xero",

                        "source_invoice_number":
                            invoice.invoice_number
                    }
                )

                db.commit()

            results.append(
                {
                    "invoice_number":
                        invoice.invoice_number,

                    "status_code":
                        response["status_code"],

                    "response":
                        response["response"]
                }
            )

        return results
    finally:
        db.close()