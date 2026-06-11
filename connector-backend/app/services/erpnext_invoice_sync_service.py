from sqlalchemy import text

from app.database import SessionLocal
from fastapi import Depends
from app.dependencies.auth import get_current_user

from app.services.erpnext_service import (
    fetch_erpnext_sales_invoices
)

from app.transformations.invoice_transform import (
    transform_erpnext_invoice
)


def sync_erpnext_invoices_service(user_id,tenant_id):

    db = SessionLocal()
    try:

        invoices = fetch_erpnext_sales_invoices(
            user_id, tenant_id
        )

        synced = []

        for invoice in invoices:

            transformed_invoice = (
                transform_erpnext_invoice(
                    invoice
                )
            )

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

            existing_invoice = db.execute(
                text("""
                    SELECT id
                    FROM unified_invoices
                    WHERE
                        tenant_id = :tenant_id
                        AND external_id = :external_id
                        AND source = 'erpnext'
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id":
                        transformed_invoice[
                            "external_id"
                        ]
                }
            ).fetchone()

            if existing_invoice:
                continue

            db.execute(
                text("""
                    INSERT INTO unified_invoices
                    (
                        tenant_id,
                        user_id,
                        source,
                        origin_system,
                        external_id,
                        invoice_number,
                        customer_name,
                        invoice_date,
                        due_date,
                        subtotal,
                        tax_amount,
                        total_amount,
                        currency,
                        status
                    )
                    VALUES
                    (
                        :tenant_id,
                        :user_id,
                        :source,
                        :origin_system,
                        :external_id,
                        :invoice_number,
                        :customer_name,
                        :invoice_date,
                        :due_date,
                        :subtotal,
                        :tax_amount,
                        :total_amount,
                        :currency,
                        :status
                    )
                """),
                {
                    "user_id": user_id,

                    "tenant_id": tenant_id,

                    "source":
                        transformed_invoice["source"],

                    "origin_system": "erpnext",

                    "external_id":
                        transformed_invoice[
                            "external_id"
                        ],

                    "invoice_number":
                        transformed_invoice[
                            "invoice_number"
                        ],

                    "customer_name":
                        transformed_invoice[
                            "customer_name"
                        ],

                    "invoice_date":
                        transformed_invoice[
                            "invoice_date"
                        ],

                    "due_date":
                        transformed_invoice[
                            "due_date"
                        ],

                    "subtotal":
                        transformed_invoice[
                            "subtotal"
                        ],

                    "tax_amount":
                        transformed_invoice[
                            "tax_amount"
                        ],

                    "total_amount":
                        transformed_invoice[
                            "total_amount"
                        ],

                    "currency":
                        transformed_invoice[
                            "currency"
                        ],

                    "status":
                        transformed_invoice[
                            "status"
                        ]
                }
            )

            synced.append(
                transformed_invoice
            )

        db.commit()

        return {
            "message":
                "ERPNext invoices synced successfully",

            "total_synced":
                len(synced),

            "invoices":
                synced
        }
    finally:
        db.close()