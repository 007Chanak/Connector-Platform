from sqlalchemy import text
from app.database import SessionLocal
import requests


def push_bill_to_xero(
    access_token,
    tenant_id,
    bill_number,
    app_tenant_id
):

    db = SessionLocal()

    try:

        bill_rows = db.execute(
            text("""
                SELECT *
                FROM unified_bills
                WHERE
                    tenant_id = :tenant_id
                    AND bill_number = :bill_number
                ORDER BY id
            """),
            {
                "tenant_id": app_tenant_id,
                "bill_number": bill_number
            }
        ).fetchall()

        if not bill_rows:

            return {
                "status_code": 404,
                "response": {
                    "error": "Bill not found"
                }
            }

        first_bill = bill_rows[0]

        line_items = []

        for row in bill_rows:

            line_items.append(
            {
                "ItemCode":
                    row.item_code,

                "Description":
                    row.item_name
                    if row.item_name
                    else row.item_code,

                "Quantity":
                    float(row.quantity)
                    if row.quantity
                    else 1,

                "UnitAmount":
                    float(row.unit_price)
                    if row.unit_price
                    else 0
            }
        )

        if not line_items:

            line_items = [
                {
                    "Description": "Migrated Bill",
                    "Quantity": 1,
                    "UnitAmount":
                        float(first_bill.total_amount)
                        if first_bill.total_amount
                        else 0
                }
            ]

        payload = {
            "Invoices": [
                {
                    "Type": "ACCPAY",

                    "InvoiceNumber":
                        first_bill.bill_number,

                    "Contact": {
                        "Name":
                            first_bill.supplier_name
                    },

                    "Date":
                        str(first_bill.bill_date),

                    "DueDate":
                        str(first_bill.due_date),

                    "Status":
                        "DRAFT",

                    "LineItems":
                        line_items
                }
            ]
        }

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                tenant_id,

            "Accept":
                "application/json",

            "Content-Type":
                "application/json"
        }

        print(
            "BILL:",
            first_bill.bill_number
        )

        print(
            "SUPPLIER:",
            first_bill.supplier_name
        )

        print(
            "XERO BILL PAYLOAD:",
            payload
        )

        response = requests.post(
            "https://api.xero.com/api.xro/2.0/Invoices",
            headers=headers,
            json=payload
        )

        try:
            response_json = response.json()
        except Exception:
            response_json = response.text

        print(
            "XERO BILL RESPONSE:",
            response_json
        )

        return {
            "status_code":
                response.status_code,

            "response":
                response_json
        }

    finally:
        db.close()

def bill_exists_in_xero(
    access_token,
    tenant_id,
    bill_number
):
    url = (
        "https://api.xero.com/api.xro/2.0/Invoices"
    )

    headers = {
        "Authorization":
            f"Bearer {access_token}",

        "Xero-tenant-id":
            tenant_id,

        "Accept":
            "application/json"
    }

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code != 200:
        return False

    invoices = response.json().get(
        "Invoices",
        []
    )

    for invoice in invoices:

        invoice_number = (
            invoice.get(
                "InvoiceNumber",
                ""
            ).strip().lower()
        )

        status = (
            invoice.get(
                "Status",
                ""
            ).upper()
        )

        if (
            invoice_number
            ==
            bill_number.strip().lower()
            and
            status != "DELETED"
        ):
            return True

    return False

def push_unified_bills_to_xero(
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

        bills = db.execute(
            text("""
                SELECT *
                FROM unified_bills
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'erpnext'
            """),
            {
                "tenant_id": app_tenant_id
            }
        ).fetchall()

        results = []

        processed_bills = set()

        for bill in bills:

            if bill.bill_number in processed_bills:
                continue

            processed_bills.add(
                bill.bill_number
            )

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :bill_number
                """),
                {
                    "tenant_id": app_tenant_id,
                    "bill_number": bill.bill_number
                }
            ).fetchone()

            if existing_migration:

                exists_in_xero = bill_exists_in_xero(
                    access_token,
                    tenant_id,
                    bill.bill_number
                )

                print(
                    "CHECKING:",
                    bill.bill_number
                )

                print(
                    "MIGRATION LOG:",
                    existing_migration
                )

                print(
                    "EXISTS IN XERO:",
                    exists_in_xero
                )

                if exists_in_xero:

                    results.append(
                        {
                            "bill_number":
                                bill.bill_number,

                            "status":
                                "Skipped - Already Migrated"
                        }
                    )

                    continue

            response = push_bill_to_xero(
                access_token,
                tenant_id,
                bill.bill_number,
                app_tenant_id
            )

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
                        "tenant_id":
                            app_tenant_id,

                        "user_id":
                            user_id,

                        "source_system":
                            "erpnext",

                        "target_system":
                            "xero",

                        "source_invoice_number":
                            bill.bill_number
                    }
                )

                db.commit()

            results.append(
                {
                    "bill_number":
                        bill.bill_number,

                    "status_code":
                        response["status_code"],

                    "response":
                        response["response"]
                }
            )

        return results

    finally:
        db.close()