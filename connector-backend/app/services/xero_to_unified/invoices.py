from sqlalchemy import text
from app.database import SessionLocal
from app.services.xero_fetch_service import (
    fetch_complete_xero_invoices
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.xero_to_unified.transformer import (
    transform_invoice_using_mapping,
    transform_invoice_item_using_mapping
)

def sync_xero_invoices_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        invoices = (
            fetch_complete_xero_invoices(
                user_id,
                tenant_id
            )
        )

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="invoices",
            source_system="xero"
        )

        invoice_item_mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="invoice_items",
            source_system="xero"
        )

        synced = []

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

        for invoice in invoices:

            if invoice.get("Type") != "ACCREC":
                continue

            valid_statuses = [
                "DRAFT",
                "AUTHORISED",
                "PAID",
                "UNPAID"
            ]

            if invoice.get("Status") not in valid_statuses:
                continue

            transformed_invoice = (
                transform_invoice_using_mapping(
                    invoice,
                    mapping
                )
            )

            print(
                "INVOICE DATA:",
                transformed_invoice
            )

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
                        transformed_invoice[
                            "external_id"
                        ]
                }
            ).fetchone()

            print(
                "SYNCING:",
                invoice.get("InvoiceNumber"),
                invoice.get("Type"),
                invoice.get("Status")
            )

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

                    "source": "xero",

                    "origin_system": "xero",

                    "external_id":
                        transformed_invoice.get(
                            "external_id"
                        ),

                    "invoice_number":
                        transformed_invoice.get(
                            "invoice_number"
                        ),

                    "customer_name":
                        transformed_invoice.get(
                            "customer_name"
                        ),

                    "invoice_date":
                        transformed_invoice.get(
                            "invoice_date"
                        ),

                    "due_date":
                        transformed_invoice.get(
                            "due_date"
                        ),

                    "subtotal":
                        transformed_invoice.get(
                            "subtotal"
                        ),

                    "tax_amount":
                        transformed_invoice.get(
                            "tax_amount"
                        ),

                    "total_amount":
                        transformed_invoice.get(
                            "total_amount"
                        ),

                    "currency":
                        transformed_invoice.get(
                            "currency"
                        ),

                    "status":
                        transformed_invoice.get(
                            "status"
                        )
                }
            )

            print(
                "INVOICE:",
                invoice.get("InvoiceNumber")
            )

            print(
                "LINE ITEMS COUNT:",
                len(
                    invoice.get(
                        "LineItems",
                        []
                    )
                )
            )

            print(
                "LINE ITEMS:",
                invoice.get(
                    "LineItems",
                    []
                )
            )

            for line_item in invoice.get(
                "LineItems",
                []
            ):

                transformed_item = (
                    transform_invoice_item_using_mapping(
                        line_item,
                        transformed_invoice[
                            "external_id"
                        ],
                        invoice_item_mapping
                    )
                )

                print(
                    "INVOICE ITEM DATA:",
                    transformed_item
                )

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
                            transformed_item.get(
                                "invoice_external_id"
                            ),

                        "item_external_id":
                            transformed_item.get(
                                "item_external_id"
                            ),

                        "item_code":
                            transformed_item.get(
                                "item_code"
                            ),

                        "item_name":
                            transformed_item.get(
                                "item_name"
                            ),

                        "quantity":
                            transformed_item.get(
                                "quantity"
                            ),

                        "unit_price":
                            transformed_item.get(
                                "unit_price"
                            ),

                        "line_total":
                            transformed_item.get(
                                "line_total"
                            )
                    }
                )

        db.commit()

        return {
            "message":
                "Invoices synced successfully",
            "total_synced":
                len(synced),
            "invoices":
                synced
        }

    finally:
        db.close()