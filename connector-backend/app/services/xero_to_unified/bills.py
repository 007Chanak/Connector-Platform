import requests
from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_auth_service import (
    refresh_xero_token
)
from fastapi import Depends
from app.dependencies.auth import get_current_user
import re
from datetime import datetime

def parse_xero_date(xero_date):

    if not xero_date:
        return None

    match = re.search(
        r"\/Date\((\d+)",
        xero_date
    )

    if not match:
        return None

    timestamp = int(match.group(1)) / 1000

    return (
        datetime
        .fromtimestamp(timestamp)
        .date()
    )

def transform_xero_bill(invoice):

    supplier_name = ""

    if invoice.get("Contact"):
        supplier_name = (
            invoice["Contact"].get("Name")
        )

    rows = []

    for line_item in invoice.get("LineItems", []):

        rows.append(
            {
                "external_id":
                    invoice.get("InvoiceID"),

                "bill_number":
                    invoice.get("InvoiceNumber"),

                "supplier_name":
                    supplier_name,

                "bill_date":
                    parse_xero_date(
                        invoice.get("Date")
                    ),

                "due_date":
                    parse_xero_date(
                        invoice.get("DueDate")
                    ),

                "item_code":
                    line_item.get("ItemCode"),

                "item_name":
                    line_item.get("Description"),

                "quantity":
                    line_item.get("Quantity"),

                "unit_price":
                    line_item.get("UnitAmount"),

                "line_amount":
                    line_item.get("LineAmount"),

                "tax_amount":
                    invoice.get("TotalTax"),

                "total_amount":
                    invoice.get("Total"),

                "status":
                    invoice.get("Status"),

                "source":
                    "xero"
            }
        )

    return rows


def sync_xero_bills_service(
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
                "tenant_id": tenant_id,
            }
        ).fetchone()

        if not integration:
            return {
                "error": "No Xero integration found"
            }

        access_token = integration.access_token
        xero_tenant_id = integration.tenant_id

        url = (
            "https://api.xero.com/api.xro/2.0/Invoices"
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

            access_token = refreshed[
                "access_token"
            ]

            headers["Authorization"] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        invoices = data.get(
            "Invoices",
            []
        )

        synced = []

        for invoice in invoices:

            if (
                invoice.get("Type")
                != "ACCPAY"
            ):
                continue

            invoice_id = invoice.get(
                "InvoiceID"
            )

            invoice_response = requests.get(
                f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}",
                headers=headers
            )

            invoice_doc = (
                invoice_response
                .json()
                .get("Invoices", [])[0]
            )
            if invoice_doc.get("Status") == "DELETED":
                continue

            print(
                "LINE ITEMS:",
                invoice_doc.get(
                    "LineItems"
                )
            )

            bills = transform_xero_bill(
                invoice_doc
            )

            for bill in bills:

                print(
                    "INSERTING:",
                    bill.get("bill_number")
                )

                existing_bill = db.execute(
                    text("""
                        SELECT id
                        FROM unified_bills
                        WHERE
                            tenant_id = :tenant_id
                            AND source = 'xero'
                            AND external_id = :external_id
                            AND line_amount = :line_amount
                            AND item_name = :item_name
                    """),
                    {
                        "tenant_id": tenant_id,
                        "external_id": bill["external_id"],
                        "item_name": bill["item_name"],
                        "line_amount": bill["line_amount"]
                    }
                ).fetchone()

                if existing_bill:

                    db.execute(
                        text("""
                            UPDATE unified_bills
                            SET
                                bill_number = :bill_number,
                                supplier_name = :supplier_name,
                                bill_date = :bill_date,
                                due_date = :due_date,
                                item_code = :item_code,
                                item_name = :item_name,
                                quantity = :quantity,
                                unit_price = :unit_price,
                                line_amount = :line_amount,
                                tax_amount = :tax_amount,
                                total_amount = :total_amount,
                                status = :status
                            WHERE id = :id
                        """),
                        {
                            "id":
                                existing_bill.id,

                            "bill_number":
                                bill.get(
                                    "bill_number"
                                ),

                            "supplier_name":
                                bill.get(
                                    "supplier_name"
                                ),

                            "bill_date":
                                bill.get(
                                    "bill_date"
                                ),

                            "due_date":
                                bill.get(
                                    "due_date"
                                ),

                            "item_code":
                                bill.get(
                                    "item_code"
                                ),

                            "item_name":
                                bill.get(
                                    "item_name"
                                ),

                            "quantity":
                                bill.get(
                                    "quantity"
                                ),

                            "unit_price":
                                bill.get(
                                    "unit_price"
                                ),

                            "line_amount":
                                bill.get(
                                    "line_amount"
                                ),

                            "tax_amount":
                                bill.get(
                                    "tax_amount"
                                ),

                            "total_amount":
                                bill.get(
                                    "total_amount"
                                ),

                            "status":
                                bill.get(
                                    "status"
                                )
                        }
                    )

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
                        "tenant_id":
                            tenant_id,

                        "user_id":
                            user_id,

                        "source":
                            bill.get(
                                "source"
                            ),

                        "external_id":
                            bill.get(
                                "external_id"
                            ),

                        "bill_number":
                            bill.get(
                                "bill_number"
                            ),

                        "supplier_name":
                            bill.get(
                                "supplier_name"
                            ),

                        "bill_date":
                            bill.get(
                                "bill_date"
                            ),

                        "due_date":
                            bill.get(
                                "due_date"
                            ),

                        "item_code":
                            bill.get(
                                "item_code"
                            ),

                        "item_name":
                            bill.get(
                                "item_name"
                            ),

                        "quantity":
                            bill.get(
                                "quantity"
                            ),

                        "unit_price":
                            bill.get(
                                "unit_price"
                            ),

                        "line_amount":
                            bill.get(
                                "line_amount"
                            ),

                        "tax_amount":
                            bill.get(
                                "tax_amount"
                            ),

                        "total_amount":
                            bill.get(
                                "total_amount"
                            ),

                        "status":
                            bill.get(
                                "status"
                            )
                    }
                )

                synced.append(
                    bill
                )

        db.commit()

        return {
            "message":
                "Xero bills synced successfully",

            "total_synced":
                len(synced),

            "bills":
                synced
        }

    finally:
        db.close()