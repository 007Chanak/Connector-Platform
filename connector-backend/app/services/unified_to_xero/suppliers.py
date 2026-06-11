from sqlalchemy import text
from app.database import SessionLocal
import requests


def push_unified_suppliers_to_xero(
    access_token,
    tenant_id,
    user_id
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

        suppliers = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'erpnext'
            """),
            {
                "tenant_id": app_tenant_id,
            }
        ).fetchall()

        synced = []

        skipped = []

        for supplier in suppliers:

            # Check if customer already exists in Xero
            existing_response = push_supplier_exists_check(
                access_token,
                tenant_id,
                supplier.supplier_name
            )

            if existing_response:

                skipped.append(
                    supplier.supplier_name
                )

                continue

            response = push_supplier_to_xero(
                access_token,
                tenant_id,
                {
                    "supplier_name":
                        supplier.supplier_name,

                    "contact_name":
                        supplier.contact_name,

                    "email":
                        supplier.email,

                    "phone":
                        supplier.phone,

                    "address":
                        supplier.address,

                    "postal_code":
                        supplier.postal_code,

                    "tax_number":
                        supplier.tax_number
                }
            )

            print("SUPPLIER:", supplier.supplier_name)
            print("CONTACT:", supplier.contact_name)
            print("XERO RESPONSE:", response)

            synced.append(
                {
                    "supplier_name":
                        supplier.supplier_name,

                    "response":
                        response
                }
            )

        return {
            "message":
                "Suppliers pushed to Xero",

            "total_synced":
                len(synced),

            "total_skipped":
                len(skipped),

            "synced_suppliers":
                synced,

            "skipped_suppliers":
                skipped
        }
    finally:
        db.close()


def push_supplier_exists_check(
    access_token,
    tenant_id,
    supplier_name
):
    url = (
        "https://api.xero.com/api.xro/2.0/Contacts"
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

    contacts = response.json().get(
        "Contacts",
        []
    )

    for contact in contacts:

        if (
            contact.get(
                "Name",
                ""
            ).strip().lower()
            ==
            supplier_name.strip().lower()
        ):
            return True

    return False

def push_supplier_to_xero(
    access_token,
    tenant_id,
    supplier
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
                "Name": supplier.get("supplier_name"),

                "IsSupplier": True,

                "EmailAddress": supplier.get("email", ""),

                "ContactPersons": [
                    {
                        "FirstName": (
                            supplier.get("contact_name", "").split(" ")[0]
                            if supplier.get("contact_name")
                            else ""
                        ),
                        "LastName": (
                            " ".join(
                                supplier.get("contact_name", "").split(" ")[1:]
                            )
                            if supplier.get("contact_name")
                            else ""
                        )
                    }
                ],

                "Phones": [
                    {
                        "PhoneType": "DEFAULT",
                        "PhoneNumber": supplier.get("phone", "")
                    }
                ],

                "Addresses": [
                    {
                        "AddressType": "POBOX",

                        "AddressLine1":
                            supplier.get("address", ""),

                        "PostalCode":
                            supplier.get("postal_code", "")
                    }
                ],

                "TaxNumber": supplier.get("tax_number", "")
            }
        ]
    }

    print(
        "XERO SUPPLIER:",
        supplier
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

    print("XERO RESPONSE:", response.json())

    return response.json()