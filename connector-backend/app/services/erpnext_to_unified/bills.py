import requests
from sqlalchemy import text
from app.database import SessionLocal


def fetch_complete_erpnext_bills(
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

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        purchase_invoices_response = requests.get(
            f"{erp.erp_url}/api/resource/Purchase Invoice",
            headers=headers
        )

        purchase_invoices = (
            purchase_invoices_response
            .json()
            .get("data", [])
        )

        unified_bills = []

        for invoice in purchase_invoices:

            invoice_name = invoice.get("name")

            invoice_doc = requests.get(
                f"{erp.erp_url}/api/resource/Purchase Invoice/{invoice_name}",
                headers=headers
            ).json()["data"]

            print(invoice_doc)

            for item in invoice_doc.get("items", []):

                bill_data = {

                    "external_id":
                        invoice_name,

                    "bill_number":
                        invoice_doc.get(
                            "bill_no"
                            )
                        or invoice_name,

                    "supplier_name":
                        invoice_doc.get(
                            "supplier"
                        ),

                    "bill_date":
                        invoice_doc.get(
                            "posting_date"
                        ),

                    "due_date":
                        invoice_doc.get(
                            "due_date"
                        ),

                    "item_code": 
                        item.get(
                            "item_code"
                        ),

                    "item_name":
                        item.get(
                            "item_name"
                        ),

                    "quantity":
                        item.get(
                            "qty"
                        ),

                    "unit_price":
                        item.get(
                            "rate"
                        ),

                    "line_amount":
                        item.get(
                            "amount"
                        ),

                    "tax_amount":
                        (
                            invoice_doc.get(
                                "total_taxes_and_charges"
                            )
                            or 0
                        ),

                    "total_amount":
                        invoice_doc.get(
                            "grand_total"
                        ),

                    "status":
                        invoice_doc.get(
                            "status"
                        )
                }

                print(
                    "APPENDING:",
                    bill_data
                )

                unified_bills.append(
                    bill_data
                )

        return unified_bills

    finally:
        db.close()

def sync_erpnext_bills_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        bills = (
            fetch_complete_erpnext_bills(
                user_id,
                tenant_id
            )
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

        for bill in bills:

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_bills
                    WHERE
                        tenant_id = :tenant_id
                        AND bill_number = :bill_number
                        AND source = 'erpnext'
                """),
                {
                    "tenant_id": tenant_id,
                    "bill_number":
                        bill["bill_number"]
                }
            ).fetchone()

            if existing:
                continue

            db.execute(
                text("""
                    INSERT INTO unified_bills
                    (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        bill_number,
                        supplier_name,
                        bill_date,
                        due_date,
                        item_code,
                        item_name,
                        quantity,
                        unit_price,
                        line_amount,
                        tax_amount,
                        total_amount,
                        status
                    )
                    VALUES
                    (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :bill_number,
                        :supplier_name,
                        :bill_date,
                        :due_date,
                        :item_code,
                        :item_name,
                        :quantity,
                        :unit_price,
                        :line_amount,
                        :tax_amount,
                        :total_amount,
                        :status
                    )
                """),
                {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "source": "erpnext",

                    "external_id":
                        bill["external_id"],

                    "bill_number":
                        bill["bill_number"],

                    "supplier_name":
                        bill["supplier_name"],

                    "bill_date":
                        bill["bill_date"],

                    "due_date":
                        bill["due_date"],
                    
                    "item_code":
                        bill["item_code"],

                    "item_name":
                        bill["item_name"],

                    "quantity":
                        bill["quantity"],

                    "unit_price":
                        bill["unit_price"],

                    "line_amount":
                        bill["line_amount"],

                    "tax_amount":
                        bill["tax_amount"],

                    "total_amount":
                        bill["total_amount"],

                    "status":
                        bill["status"]
                }
            )

            synced.append(
                bill
            )

        db.commit()

        return {
            "message":
                "ERPNext bills synced successfully",
            "total_synced":
                len(synced),
            "bills":
                synced
        }

    finally:
        db.close()