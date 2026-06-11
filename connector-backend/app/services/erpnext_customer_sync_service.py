from sqlalchemy import text
from fastapi import Depends

from app.database import SessionLocal
from app.dependencies.auth import get_current_user

from app.services.erpnext_service import (
    fetch_complete_erpnext_customers
)


def sync_erpnext_customers_service(
    user_id,tenant_id
):

    db = SessionLocal()
    try:

        customers = (
            fetch_complete_erpnext_customers(
                user_id, tenant_id
            )
        )

        synced = []

        for customer in customers:

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
                    "tenant_id": tenant_id,
                    "customer_name":
                        customer["customer_name"]
                }
            ).fetchone()

            print(
                "EXISTING CHECK:",
                customer["customer_name"],
                existing
            )

            if existing:
                continue

            print(
                "INSERTING:",
                customer
            )

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
                        postal_code
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
                        :postal_code
                    )
                """),
                {
                    "user_id": user_id,
                    "source": "erpnext",
                    "tenant_id": tenant_id,

                    "external_id":
                        customer["customer_name"],

                    "customer_name":
                        customer["customer_name"],
                    
                    "contact_name":
                        customer["contact_name"],

                    "email":
                        customer["email"],

                    "phone":
                        customer["phone"],

                    "address":
                        customer["address"],
                    
                    "postal_code": customer["postal_code"]
                }
            )

            synced.append(
                customer
            )

        db.commit()

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