import requests
from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_auth_service import (
    refresh_xero_token
)

from app.transformations.invoice_transform import (
    transform_xero_invoice
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def fetch_xero_invoices(user_id,tenant_id):

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

        url = "https://api.xero.com/api.xro/2.0/Invoices"

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

            access_token = refreshed["access_token"]

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

        data = response.json()

        print("INVOICES KEY:", data.get("Invoices"))

        invoices = data.get("Invoices", [])

        for invoice in invoices:

            if invoice.get("InvoiceNumber") == "INV-001":

                print("\n========== INV-001 ==========")
                print(invoice)
                print("=============================\n")

                break
        
        print("TOTAL XERO INVOICES:", len(invoices))

        synced = []

        valid_statuses = [
            "DRAFT",
            "AUTHORISED",
            "PAID",
            "UNPAID"
        ]

        for invoice in invoices:

            if invoice.get("Status") not in valid_statuses:
                continue

            transformed_invoice = (
                transform_xero_invoice(invoice)
            )

            invoice_id = invoice.get(
                "InvoiceID"
            )

            detail_url = (
                f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}"
            )

            detail_response = requests.get(
                detail_url,
                headers=headers
            )

            invoice_details = (
                detail_response.json()
                .get("Invoices", [{}])[0]
            )

            print(
                "DETAILED LINE ITEMS:",
                invoice_details.get(
                    "LineItems",
                    []
                )
            )

            print(
                "PROCESSING:",
                transformed_invoice["invoice_number"]
            )

            existing_erp_invoice = db.execute(
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
                    "tenant_id": tenant_id,
                    "invoice_number":
                        transformed_invoice["invoice_number"]
                }
            ).fetchone()

            if existing_erp_invoice:

                print(
                    "SKIPPED ERP-ORIGIN INVOICE:",
                    transformed_invoice["invoice_number"]
                )

                continue

            existing_invoice = db.execute(
                text("""
                    SELECT id
                    FROM unified_invoices
                    WHERE
                        tenant_id = :tenant_id
                        AND external_id = :external_id
                        AND source = 'xero'
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id":
                        transformed_invoice["external_id"]
                }
            ).fetchone()

            if existing_invoice:

                print(
                    "SKIPPED EXISTING INVOICE:",
                    transformed_invoice["invoice_number"]
                )

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
                    
                    "origin_system": "xero",

                    "external_id":
                        transformed_invoice["external_id"],

                    "invoice_number":
                        transformed_invoice["invoice_number"],

                    "customer_name":
                        transformed_invoice["customer_name"],

                    "invoice_date":
                        transformed_invoice["invoice_date"],

                    "due_date":
                        transformed_invoice["due_date"],

                    "subtotal":
                        transformed_invoice["subtotal"],

                    "tax_amount":
                        transformed_invoice["tax_amount"],

                    "total_amount":
                        transformed_invoice["total_amount"],

                    "currency":
                        transformed_invoice["currency"],

                    "status":
                        transformed_invoice["status"]
                }
            )

            # SAVE INVOICE LINE ITEMS

            print(
                "INVOICE:",
                invoice.get("InvoiceNumber")
            )

            print(
                "LINE ITEMS:",
                invoice.get("LineItems")
            )

            for line_item in invoice_details.get(
                "LineItems",
                []
            ):

                db.execute(
                    text("""
                        INSERT INTO unified_invoice_items
                        (
                            tenant_id,
                            user_id,
                            source,
                            invoice_external_id,
                            item_external_id,
                            item_code,
                            item_name,
                            quantity,
                            unit_price,
                            line_total
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source,
                            :invoice_external_id,
                            :item_external_id,
                            :item_code,
                            :item_name,
                            :quantity,
                            :unit_price,
                            :line_total
                        )
                    """),
                    {
                        "user_id": user_id,

                        "tenant_id": tenant_id,

                        "source": "xero",

                        "invoice_external_id":
                            transformed_invoice[
                                "external_id"
                            ],

                        "item_external_id":
                            line_item.get(
                                "LineItemID"
                            ),

                        "item_code":
                            line_item.get(
                                "ItemCode",
                                ""
                            ),

                        "item_name":
                            line_item.get(
                                "Description",
                                ""
                            ),

                        "quantity":
                            line_item.get(
                                "Quantity",
                                1
                            ),

                        "unit_price":
                            line_item.get(
                                "UnitAmount",
                                0
                            ),

                        "line_total":
                            line_item.get(
                                "LineAmount",
                                0
                            )
                    }
                )

            synced.append(
                transformed_invoice
            )

        db.commit()

        return {
            "message": "Invoices synced successfully",
            "total_synced": len(synced),
            "invoices": synced
        }
    finally:
        db.close()