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

        print("=" * 80)
        print("PUSHING UNIFIED SUPPLIERS TO XERO")
        print("=" * 80)

        suppliers = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'erpnext'
            """),
            {
                "tenant_id": app_tenant_id
            }
        ).fetchall()

        print("SUPPLIERS FOUND:", len(suppliers))

        synced = []
        skipped = []

        for supplier in suppliers:

            print()
            print("=" * 80)
            print("PROCESSING SUPPLIER")
            print(supplier.supplier_name)
            print("=" * 80)

            existing_response = push_supplier_exists_check(
                access_token,
                tenant_id,
                supplier.supplier_name
            )

            if existing_response:

                print(
                    "SKIPPED - ALREADY EXISTS:",
                    supplier.supplier_name
                )

                skipped.append(
                    supplier.supplier_name
                )

                continue

            supplier_payload = {
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
                    supplier.tax_number,

                "city":
                    supplier.city,

                "state":
                    supplier.state,

                "country":
                    supplier.country
            }

            print("UNIFIED SUPPLIER:")
            print(supplier_payload)

            response = push_supplier_to_xero(
                access_token,
                tenant_id,
                supplier_payload
            )

            synced.append(
                {
                    "supplier_name":
                        supplier.supplier_name,

                    "response":
                        response
                }
            )

        print()
        print("=" * 80)
        print("SUPPLIER PUSH COMPLETE")
        print("TOTAL SYNCED:", len(synced))
        print("TOTAL SKIPPED:", len(skipped))
        print("=" * 80)

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

    print(
        "SUPPLIER EXISTS STATUS:",
        response.status_code
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

            print(
                "SUPPLIER EXISTS IN XERO:",
                supplier_name
            )

            return True

    return False


def push_supplier_to_xero(
    access_token,
    tenant_id,
    supplier
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
            "application/json",

        "Content-Type":
            "application/json"
    }

    contact_name = (
        supplier.get(
            "contact_name"
        )
        or ""
    ).strip()

    first_name = ""
    last_name = ""

    if contact_name:

        parts = contact_name.split()

        first_name = parts[0]

        if len(parts) > 1:

            last_name = " ".join(
                parts[1:]
            )

    payload = {
        "Contacts": [
            {
                "Name":
                    supplier.get(
                        "supplier_name"
                    ),

                "IsSupplier":
                    True,

                "EmailAddress":
                    supplier.get(
                        "email",
                        ""
                    ),

                "ContactPersons": [
                    {
                        "FirstName":
                            first_name,

                        "LastName":
                            last_name
                    }
                ],

                "Phones": [
                    {
                        "PhoneType":
                            "DEFAULT",

                        "PhoneNumber":
                            supplier.get(
                                "phone",
                                ""
                            )
                    }
                ],

                "Addresses": [
                    {
                        "AddressType":
                            "POBOX",

                        "AddressLine1":
                            supplier.get(
                                "address",
                                ""
                            ),

                        "City":
                            supplier.get(
                                "city",
                                ""
                            ),

                        "Region":
                            supplier.get(
                                "state",
                                ""
                            ),

                        "Country":
                            supplier.get(
                                "country",
                                ""
                            ),

                        "PostalCode":
                            supplier.get(
                                "postal_code",
                                ""
                            )
                    }
                ],

                "TaxNumber":
                    supplier.get(
                        "tax_number",
                        ""
                    )
            }
        ]
    }

    print()
    print("=" * 80)
    print("XERO SUPPLIER PAYLOAD")
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

    print()
    print("=" * 80)
    print("XERO RESPONSE STATUS")
    print(response.status_code)
    print("XERO RESPONSE BODY")
    print(response_json)
    print("=" * 80)

    return response_json