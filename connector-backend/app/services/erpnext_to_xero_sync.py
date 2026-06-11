import requests

from sqlalchemy import text

from app.database import SessionLocal

from app.services.erpnext_service import (
    fetch_complete_erpnext_customers
)

from app.services.xero_push_service import (
    push_customer_to_xero
)
from fastapi import Depends
from app.dependencies.auth import get_current_user



def sync_erpnext_to_xero(user_id,tenant_id):

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
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
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

        # FETCH COMPLETE ERP CUSTOMERS
        erp_customers = fetch_complete_erpnext_customers(
            user_id, tenant_id
        )

        # FETCH EXISTING XERO CONTACTS
        xero_url = "https://api.xero.com/api.xro/2.0/Contacts"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": xero_tenant_id,
            "Accept": "application/json"
        }

        xero_response = requests.get(
            xero_url,
            headers=headers
        )

        xero_data = xero_response.json()

        existing_xero_contacts = set()

        for contact in xero_data.get("Contacts", []):

            existing_xero_contacts.add(
                contact.get(
                    "Name",
                    ""
                ).strip().lower()
            )

        synced = []

        skipped = []

        for customer in erp_customers:

            customer_name = customer.get(
                "customer_name",
                ""
            ).strip()

            if not customer_name:
                continue

            if (
                customer_name.lower()
                in existing_xero_contacts
            ):

                skipped.append(
                    {
                        "customer_name": customer_name,
                        "reason": "Already exists in Xero"
                    }
                )

                continue

            transformed_customer = {
                "customer_name": customer_name,

                "contact_name": customer.get(
                    "contact_name",
                    ""
                ),

                "email": customer.get(
                    "email",
                    ""
                ),

                "phone": customer.get(
                    "phone",
                    ""
                ),

                "address": customer.get(
                    "address",
                    ""
                ),

                "postal_code": customer.get(
                    "postal_code",
                    ""
                ),

                "tax_number": customer.get(
                    "tax_number",
                    ""
                )
            }

            print(
                "SENDING TO XERO:",
                transformed_customer
            )

            response = push_customer_to_xero(
                access_token,
                tenant_id,
                transformed_customer
            )

            synced.append(
                {
                    "customer_name": customer_name,
                    "response": response
                }
            )

        return {
            "message": "ERPNext customers pushed to Xero",
            "total_synced": len(synced),
            "total_skipped": len(skipped),
            "synced_customers": synced,
            "skipped_customers": skipped
        }
    finally:
        db.close()