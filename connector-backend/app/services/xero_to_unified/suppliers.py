import requests
from sqlalchemy import text
from app.database import SessionLocal
from datetime import datetime

from app.services.xero_auth_service import (
    refresh_xero_token
)
from fastapi import Depends
from app.dependencies.auth import get_current_user

from app.services.xero_to_unified.transformer import (
    transform_supplier_using_mapping
)

from app.services.mapping_service import (
    get_mapping_dict
)


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

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="suppliers",
            source_system="xero"
        )

        synced = []

        for contact in contacts:
            if not contact.get("IsSupplier"):
                continue

            if contact.get("ContactStatus") != "ACTIVE":
                continue

            supplier = (
                transform_supplier_using_mapping(
                    contact,
                    mapping
                )
            )

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
                            city = :city,
                            state = :state,
                            country = :country,
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

                        "city": supplier.get("city"),

                        "state": supplier.get("state"),

                        "country": supplier.get("country"),

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
                        city,
                        state,
                        country,
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
                        :city,
                        :state,
                        :country,
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

                    "source": "xero",

                    "external_id": supplier.get("external_id"),

                    "supplier_name": supplier.get("supplier_name"),

                    "contact_name": supplier.get("contact_name"),

                    "email": supplier.get("email"),

                    "phone": supplier.get("phone"),

                    "address": supplier.get("address"),

                    "city": supplier.get("city"),

                    "state": supplier.get("state"),

                    "country": supplier.get("country"),

                    "postal_code": supplier.get("postal_code"),

                    "tax_number": supplier.get("tax_number"),

                    "website": supplier.get("website"),

                    "status": supplier.get("status"),

                    "created_at": datetime.utcnow()
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