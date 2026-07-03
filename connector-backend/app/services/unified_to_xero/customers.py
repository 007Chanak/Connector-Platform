from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_push_service import (
    push_customer_to_xero
)


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
                "tenant_id":
                    app_tenant_id
            }
        ).fetchall()

        print("=" * 80)
        print("UNIFIED CUSTOMERS FOUND")
        print(len(customers))
        print("=" * 80)

        synced = []

        skipped = []

        for customer in customers:

            print("\n")
            print("=" * 80)
            print("PROCESSING CUSTOMER")
            print(customer.customer_name)
            print("=" * 80)

            migration_check = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :customer_name
                """),
                {
                    "tenant_id":
                        app_tenant_id,

                    "customer_name":
                        customer.customer_name
                }
            ).fetchone()

            print(
                "MIGRATION CHECK:",
                migration_check
            )

            if migration_check:

                skipped.append(
                    {
                        "customer_name":
                            customer.customer_name,

                        "reason":
                            "Already Migrated"
                    }
                )

                continue

            exists_in_xero = (
                push_customer_exists_check(
                    access_token,
                    tenant_id,
                    customer.customer_name
                )
            )

            print(
                "XERO EXISTS CHECK:",
                exists_in_xero
            )

            if exists_in_xero:

                skipped.append(
                    {
                        "customer_name":
                            customer.customer_name,

                        "reason":
                            "Already Exists In Xero"
                    }
                )

                continue

            payload = {

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
                    customer.tax_number,

                "website":
                    customer.website,

                "city":
                    customer.city,

                "state":
                    customer.state,

                "country":
                    customer.country,

                "status":
                    customer.status
            }

            print("=" * 80)
            print("XERO CUSTOMER PAYLOAD")
            print(payload)
            print("=" * 80)

            response = push_customer_to_xero(
                access_token,
                tenant_id,
                payload
            )

            print("=" * 80)
            print("XERO RESPONSE")
            print(response)
            print("=" * 80)

            success = False

            if isinstance(response, dict):

                if response.get("Contacts"):

                    success = True

            if success:

                db.execute(
                    text("""
                        INSERT INTO migration_logs
                        (
                            tenant_id,
                            user_id,
                            source_system,
                            target_system,
                            source_invoice_number
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source_system,
                            :target_system,
                            :source_invoice_number
                        )
                    """),
                    {
                        "tenant_id":
                            app_tenant_id,

                        "user_id":
                            user_id,

                        "source_system":
                            "erpnext",

                        "target_system":
                            "xero",

                        "source_invoice_number":
                            customer.customer_name
                    }
                )

                db.commit()

            synced.append(
                {
                    "customer_name":
                        customer.customer_name,

                    "response":
                        response
                }
            )

        print("\n")
        print("=" * 80)
        print("FINAL RESULTS")
        print(
            {
                "synced":
                    len(synced),

                "skipped":
                    len(skipped)
            }
        )
        print("=" * 80)

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

    print("=" * 80)
    print("XERO CONTACT CHECK")
    print(response.status_code)
    print("=" * 80)

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