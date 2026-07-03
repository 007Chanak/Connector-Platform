import requests
import json
from sqlalchemy import text
from app.database import SessionLocal
from datetime import datetime
from app.transformations.customer_transform import (
    transform_xero_contact
)
from app.services.xero_auth_service import (
    refresh_xero_token
)
from app.services.xero_to_unified.transformer import (
    transform_customer_using_mapping
)
from app.services.mapping_service import (
    get_mapping_dict
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def sync_xero_customers_service(user_id,tenant_id):

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

            print("CONTACT PERSONS:")
            print(contact.get("ContactPersons"))

            
            print(
                json.dumps(
                    contact,
                    indent=4
                )
            )            

            mapping = get_mapping_dict(
                tenant_id=tenant_id,
                entity_type="customers",
                source_system="xero"
            )

            customer = (
                transform_customer_using_mapping(
                    contact,
                    mapping
                )
            )

            print(
                "INSERTING:",
                customer.get("customer_name"),
                customer.get("postal_code")
            )

            synced.append(customer)

            existing_customer = db.execute(
                text("""
                    SELECT id
                    FROM unified_customers
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

            if existing_customer:

                db.execute(
                    text("""
                        UPDATE unified_customers
                        SET
                            customer_name = :customer_name,
                            contact_name = :contact_name,
                            email = :email,
                            phone = :phone,
                            address = :address,
                            postal_code = :postal_code,
                            tax_number = :tax_number,
                            website = :website,
                            status = :status,
                            city = :city,
                            state = :state,
                            country = :country
                        WHERE id = :id
                    """),
                    {
                        "id": existing_customer.id,
                        "customer_name": customer.get("customer_name"),
                        "contact_name": customer.get("contact_name"),
                        "email": customer.get("email"),
                        "phone": customer.get("phone"),
                        "address": customer.get("address"),
                        "postal_code": customer.get("postal_code"),
                        "tax_number": customer.get("tax_number"),
                        "website": customer.get("website"),
                        "status": customer.get("status"),
                        "city": customer.get("city"),
                        "state": customer.get("state"),
                        "country": customer.get("country"),
                    }
                )

                continue

            db.execute(
                text("""
                    INSERT INTO unified_customers (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        customer_name,
                        contact_name,
                        email,
                        phone,
                        address,
                        postal_code,
                        tax_number,
                        website,
                        status,
                        city,
                        state,
                        country,
                        created_at
                    )
                    VALUES (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :customer_name,
                        :contact_name,
                        :email,
                        :phone,
                        :address,
                        :postal_code,
                        :tax_number,
                        :website,
                        :status,
                        :city,
                        :state,
                        :country,
                        :created_at
                    )
                """),
                {
                    "user_id": user_id,
                    
                    "tenant_id": tenant_id,

                    "source": "xero",

                    "external_id": customer.get("external_id"),

                    "customer_name": customer.get("customer_name"),

                    "contact_name": customer.get("contact_name"),

                    "email": customer.get("email"),

                    "phone": customer.get("phone"),

                    "address": customer.get("address"),

                    "postal_code": customer.get("postal_code"),

                    "tax_number": customer.get("tax_number"),

                    "website": customer.get("website"),

                    "status": customer.get("status"),

                    "city": customer.get("city"),

                    "state": customer.get("state"),

                    "country": customer.get("country"),

                    "created_at": datetime.utcnow()
                }
            )

        db.commit()

        return {
            "message": "Xero customers synced successfully",
            "total_synced": len(synced),
            "customers": synced
        }
    finally:
        db.close()