import requests


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

def push_item_to_xero(
    access_token,
    tenant_id,
    item
):

    url = "https://api.xero.com/api.xro/2.0/Items"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "Items": [
            {
                "Code":
                    item.item_code,

                "Name":
                    item.item_name,

                "Description":
                    item.description or "",

                "IsSold": True
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