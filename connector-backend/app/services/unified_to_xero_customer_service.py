from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_push_service import (
    push_customer_to_xero
)
from fastapi import Depends
from app.dependencies.auth import get_current_user


def push_unified_customers_to_xero(
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

        customers = db.execute(
            text("""
                SELECT *
                FROM unified_customers
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

        for customer in customers:

            # Check if customer already exists in Xero
            existing_response = push_customer_exists_check(
                access_token,
                tenant_id,
                customer.customer_name
            )

            if existing_response:

                skipped.append(
                    customer.customer_name
                )

                continue

            response = push_customer_to_xero(
                access_token,
                tenant_id,
                {
                    "customer_name":
                        customer.customer_name,

                    "contact_name":
                        customer.contact_name,

                    "email":
                        customer.email,

                    "phone":
                        customer.phone,

                    "address":
                        customer.address,

                    "postal_code":
                        customer.postal_code,

                    "tax_number":
                        customer.tax_number
                }
            )

            print("CUSTOMER:", customer.customer_name)
            print("CONTACT:", customer.contact_name)
            print("XERO RESPONSE:", response)

            synced.append(
                {
                    "customer_name":
                        customer.customer_name,

                    "response":
                        response
                }
            )

        return {
            "message":
                "Customers pushed to Xero",

            "total_synced":
                len(synced),

            "total_skipped":
                len(skipped),

            "synced_customers":
                synced,

            "skipped_customers":
                skipped
        }
    finally:
        db.close()


def push_customer_exists_check(
    access_token,
    tenant_id,
    customer_name
):

    import requests

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
            customer_name.strip().lower()
        ):
            return True

    return False