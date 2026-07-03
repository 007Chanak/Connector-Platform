from sqlalchemy import text

from app.database import SessionLocal

from app.services.erpnext_fetch_service import (
    fetch_complete_erpnext_customers
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.erpnext_to_unified.transformer import (
    transform_erpnext_customer_using_mapping
)


def sync_erpnext_customers_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        customers = (
            fetch_complete_erpnext_customers(
                user_id,
                tenant_id
            )
        )

        mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="customers",
            source_system="erpnext"
        )

        print("=" * 80)
        print("ERPNEXT CUSTOMER MAPPING")
        print(mapping)
        print("=" * 80)

        synced = []

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

        print("=" * 80)
        print("ERPNEXT CUSTOMERS FOUND")
        print(len(customers))
        print("=" * 80)

        for customer in customers:

            print("\n")
            print("=" * 80)
            print("RAW ERPNEXT CUSTOMER")
            print(customer)
            print("=" * 80)

            transformed_customer = (
                transform_erpnext_customer_using_mapping(
                    customer,
                    mapping
                )
            )

            print("=" * 80)
            print("TRANSFORMED CUSTOMER")
            print(transformed_customer)
            print("=" * 80)

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_customers
                    WHERE
                        tenant_id = :tenant_id
                        AND customer_name = :customer_name
                        AND source = 'erpnext'
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "customer_name":
                        transformed_customer.get(
                            "customer_name"
                        )
                }
            ).fetchone()

            print(
                "EXISTING CHECK:",
                transformed_customer.get(
                    "customer_name"
                ),
                existing
            )

            if existing:

                print(
                    "SKIPPED - ALREADY EXISTS"
                )

                continue

            print("=" * 80)
            print("INSERTING CUSTOMER")
            print(transformed_customer)
            print("=" * 80)

            db.execute(
                text("""
                    INSERT INTO unified_customers
                    (
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
                        city,
                        state,
                        country,
                        tax_number,
                        website,
                        status
                    )
                    VALUES
                    (
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
                        :city,
                        :state,
                        :country,
                        :tax_number,
                        :website,
                        :status
                    )
                """),
                {
                    "tenant_id":
                        tenant_id,

                    "user_id":
                        user_id,

                    "source":
                        "erpnext",

                    "external_id":
                        transformed_customer.get(
                            "external_id"
                        ),

                    "customer_name":
                        transformed_customer.get(
                            "customer_name"
                        ),

                    "contact_name":
                        transformed_customer.get(
                            "contact_name"
                        ),

                    "email":
                        transformed_customer.get(
                            "email"
                        ),

                    "phone":
                        transformed_customer.get(
                            "phone"
                        ),

                    "address":
                        transformed_customer.get(
                            "address"
                        ),

                    "postal_code":
                        transformed_customer.get(
                            "postal_code"
                        ),

                    "city":
                        transformed_customer.get(
                            "city"
                        ),

                    "state":
                        transformed_customer.get(
                            "state"
                        ),

                    "country":
                        transformed_customer.get(
                            "country"
                        ),

                    "tax_number":
                        transformed_customer.get(
                            "tax_number"
                        ),

                    "website":
                        transformed_customer.get(
                            "website"
                        ),

                    "status":
                        transformed_customer.get(
                            "status"
                        )
                }
            )

            synced.append(
                transformed_customer
            )

        db.commit()

        print("\n")
        print("=" * 80)
        print("SYNC COMPLETE")
        print("TOTAL SYNCED:", len(synced))
        print("=" * 80)

        return {

            "message":
                "ERPNext customers synced successfully",

            "total_synced":
                len(synced),

            "customers":
                synced
        }

    finally:

        db.close()