import requests
from sqlalchemy import text
from app.database import SessionLocal

from app.services.xero_auth_service import (
    refresh_xero_token
)
from fastapi import Depends
from app.dependencies.auth import get_current_user

def transform_xero_supplier(contact):

    phone = ""

    phones = contact.get("Phones", [])

    for p in phones:
        if p.get("PhoneNumber"):
            phone = p.get("PhoneNumber")
            break

    address = ""
    address_obj = None
    postal_code = ""

    for addr in contact.get("Addresses", []):

        if (
            addr.get("AddressLine1")
            or addr.get("City")
            or addr.get("Region")
            or addr.get("Country")
        ):
            address_obj = addr
            break

    if address_obj:

        postal_code = (
            address_obj.get("PostalCode")
            or ""
        )

        address_parts = []

        if address_obj.get("AddressLine1"):
            address_parts.append(
                address_obj["AddressLine1"]
            )

        if address_obj.get("City"):
            address_parts.append(
                address_obj["City"]
            )

        if address_obj.get("Region"):
            address_parts.append(
                address_obj["Region"]
            )

        if address_obj.get("Country"):
            address_parts.append(
                address_obj["Country"]
            )

        address = ", ".join(address_parts)

    contact_name = " ".join(
        filter(
            None,
            [
                contact.get("FirstName"),
                contact.get("LastName")
            ]
        )
    )

    if not contact_name:
        contact_name = contact.get("Name", "")

    return {

        "external_id": contact.get("ContactID"),

        "supplier_name": contact.get("Name"),

        "contact_name": contact_name,

        "email": contact.get("EmailAddress"),

        "phone": phone,

        "address": address,

        "postal_code": postal_code,

        "tax_number": contact.get("TaxNumber"),

        "website": contact.get("Website"),

        "status": contact.get("ContactStatus"),

        "created_at": None,

        "source": "xero"
    }


def sync_xero_suppliers_service(user_id,tenant_id):

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

        url = "https://api.xero.com/api.xro/2.0/Contacts"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": xero_tenant_id,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)

        data = response.json()

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
        print(data)
        contacts = data.get("Contacts", [])

        synced = []

        for contact in contacts:
            if not contact.get("IsSupplier"):
                continue

            if contact.get("ContactStatus") != "ACTIVE":
                continue

            supplier = transform_xero_supplier(contact)

            print(
                "INSERTING:",
                supplier.get("supplier_name"),
                supplier.get("postal_code")
            )

            synced.append(supplier)

            print(
                "SUPPLIER DATA:",
                supplier
            )

            existing_supplier = db.execute(
                text("""
                    SELECT id
                    FROM unified_suppliers
                    WHERE
                        tenant_id = :tenant_id
                        AND external_id = :external_id
                        AND source = :source
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id": contact.get("ContactID"),
                    "source": "xero"
                }
            ).fetchone()


            if existing_supplier:

                db.execute(
                    text("""
                        UPDATE unified_suppliers
                        SET
                            supplier_name = :supplier_name,
                            contact_name = :contact_name,
                            email = :email,
                            phone = :phone,
                            address = :address,
                            postal_code = :postal_code,
                            tax_number = :tax_number,
                            website = :website,
                            status = :status
                        WHERE id = :id
                    """),
                    {
                        "id": existing_supplier.id,
                        "supplier_name": supplier.get("supplier_name"),
                        "contact_name": supplier.get("contact_name"),
                        "email": supplier.get("email"),
                        "phone": supplier.get("phone"),
                        "address": supplier.get("address"),
                        "postal_code": supplier.get("postal_code"),
                        "tax_number": supplier.get("tax_number"),
                        "website": supplier.get("website"),
                        "status": supplier.get("status")
                    }
                )

                continue

            db.execute(
                text("""
                    INSERT INTO unified_suppliers (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        supplier_name,
                        contact_name,
                        email,
                        phone,
                        address,
                        postal_code,
                        tax_number,
                        website,
                        status,
                        created_at
                    )
                    VALUES (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :supplier_name,
                        :contact_name,
                        :email,
                        :phone,
                        :address,
                        :postal_code,
                        :tax_number,
                        :website,
                        :status,
                        :created_at
                    )
                """),
                {
                    "user_id": user_id,
                    
                    "tenant_id": tenant_id,

                    "source": supplier.get("source"),

                    "external_id": supplier.get("external_id"),

                    "supplier_name": supplier.get("supplier_name"),

                    "contact_name": supplier.get("contact_name"),

                    "email": supplier.get("email"),

                    "phone": supplier.get("phone"),

                    "address": supplier.get("address"),

                    "postal_code": supplier.get("postal_code"),

                    "tax_number": supplier.get("tax_number"),

                    "website": supplier.get("website"),

                    "status": supplier.get("status"),

                    "created_at": supplier.get("created_at")
                }
            )

        db.commit()

        return {
            "message": "Xero Suppliers synced successfully",
            "total_synced": len(synced),
            "suppliers": synced
        }
    finally:
        db.close()