import requests
from sqlalchemy import text

from app.database import SessionLocal


def get_xero_default_accounts(
    tenant_id
):

    db = SessionLocal()

    try:

        sales_account = db.execute(
            text("""
                SELECT account_code
                FROM unified_accounts
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
                    AND account_type = 'REVENUE'
                ORDER BY id
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        purchase_account = db.execute(
            text("""
                SELECT account_code
                FROM unified_accounts
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
                    AND (
                        account_name = 'Cost of Goods Sold'
                        OR
                        account_code = '310'
                    )
                ORDER BY id
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        return {

            "sales_account_code":
                sales_account.account_code
                if sales_account
                else "200",

            "purchase_account_code":
                purchase_account.account_code
                if purchase_account
                else "310"
        }

    finally:

        db.close()

def push_customer_to_xero(
    access_token,
    tenant_id,
    customer
):

    url = "https://api.xero.com/api.xro/2.0/Contacts"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "Contacts": [
            {
                "Name": customer.get("customer_name"),

                "EmailAddress": customer.get("email", ""),

                "ContactPersons": [
                    {
                        "FirstName": (
                            customer.get("contact_name", "").split(" ")[0]
                            if customer.get("contact_name")
                            else ""
                        ),
                        "LastName": (
                            " ".join(
                                customer.get("contact_name", "").split(" ")[1:]
                            )
                            if customer.get("contact_name")
                            else ""
                        )
                    }
                ],

                "Phones": [
                    {
                        "PhoneType": "DEFAULT",
                        "PhoneNumber": customer.get("phone", "")
                    }
                ],

                "Addresses": [
                    {
                        "AddressType": "POBOX",

                        "AddressLine1":
                            customer.get("address", ""),

                        "PostalCode":
                            customer.get("postal_code", "")
                    }
                ],

                "TaxNumber": customer.get("tax_number", "")
            }
        ]
    }

    print(
        "XERO CUSTOMER:",
        customer
    )

    print(
        "XERO PAYLOAD:",
        payload
    )

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()

def push_invoice_to_xero(
    access_token,
    tenant_id,
    invoice
):

    url = "https://api.xero.com/api.xro/2.0/Invoices"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "Invoices": [
            {
                "Type": "ACCREC",

                "InvoiceNumber": invoice.invoice_number,

                "Contact": {
                    "Name": invoice.customer_name
                },

                "DateString":
                    str(
                        invoice.invoice_date
                    ),

                "DueDateString":
                    str(
                        invoice.due_date
                    ),

                "Status": "DRAFT",

                "LineItems": [
                    {
                        "Description":
                            invoice.invoice_number,

                        "Quantity": 1,

                        "UnitAmount":
                            float(
                                invoice.total_amount
                            )
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return {
        "status_code":
            response.status_code,

        "response":
            response.json()
    }

import requests


def push_item_to_xero(
    access_token,
    tenant_id,
    item_payload,
    app_tenant_id
):

    accounts = get_xero_default_accounts(
        app_tenant_id
    )

    sales_account_code = (
        accounts[
            "sales_account_code"
        ]
    )

    purchase_account_code = (
        accounts[
            "purchase_account_code"
        ]
    )

    url = (
        "https://api.xero.com/api.xro/2.0/Items"
    )

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

    payload = {
        "Items": [
            {
                "Code":
                    item_payload.get(
                        "Code"
                    ),

                "Name":
                    item_payload.get(
                        "Name"
                    ),

                "Description":
                    item_payload.get(
                        "Description",
                        ""
                    ),

                "IsSold":
                    item_payload.get(
                        "IsSold",
                        True
                    ),

                "IsPurchased":
                    item_payload.get(
                        "IsPurchased",
                        True
                    ),

                "SalesDetails": {

                    "UnitPrice":
                        float(
                            item_payload.get(
                                "SalesUnitPrice",
                                0
                            )
                        ),

                    "AccountCode":
                        sales_account_code
                },

                "PurchaseDetails": {

                    "UnitPrice":
                        float(
                            item_payload.get(
                                "PurchaseUnitPrice",
                                0
                            )
                        ),

                    "AccountCode":
                        purchase_account_code
                }
            }
        ]
    }

    print("=" * 80)
    print("SALES ACCOUNT CODE")
    print(sales_account_code)

    print("PURCHASE ACCOUNT CODE")
    print(purchase_account_code)

    print("FINAL XERO ITEM PAYLOAD")
    print(payload)
    print("=" * 80)

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    try:

        response_json = response.json()

    except Exception:

        response_json = response.text

    print("=" * 80)
    print("XERO ITEM RESPONSE STATUS")
    print(response.status_code)

    print("XERO ITEM RESPONSE")
    print(response_json)
    print("=" * 80)

    return response_json

def push_item_exists_check(
    access_token,
    tenant_id,
    item_code
):

    import requests

    url = (
        "https://api.xero.com/api.xro/2.0/Items"
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

    print(
        "ITEM EXISTS STATUS:",
        response.status_code
    )

    if response.status_code != 200:

        return False

    items = response.json().get(
        "Items",
        []
    )

    for existing_item in items:

        if (
            existing_item.get(
                "Code",
                ""
            ).strip().lower()
            ==
            str(item_code).strip().lower()
        ):

            print(
                "ITEM EXISTS IN XERO:",
                item_code
            )

            return True

    return False

def invoice_exists_in_xero(
    access_token,
    tenant_id,
    invoice_number
):

    import requests

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

    print(
        "CHECKING XERO FOR:",
        invoice_number
    )

    for invoice in invoices:

        print(
            "FOUND:",
            invoice.get("InvoiceNumber")
        )

        if (
            invoice.get("InvoiceNumber") == invoice_number
            and
            invoice.get("Status") not in [
                "DELETED",
                "VOIDED"
            ]
        ):

            print(
                "MATCHED:",
                invoice_number
            )

            return True

    return False