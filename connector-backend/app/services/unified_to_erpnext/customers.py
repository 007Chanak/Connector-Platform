import requests
from sqlalchemy import text
from app.database import SessionLocal

from app.services.mapping_service import (
    build_payload_from_mapping,
    get_target_mappings
)

def push_customers_to_erpnext(user_id,tenant_id):

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

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchone()

        if not erp:
            return {
                "error": "No ERPNext integration found"
            }
        
        target_mappings = get_target_mappings(
            tenant_id=tenant_id,
            entity_type="customers",
            target_system="erpnext"
        )

        customers = db.execute(
            text("""
                SELECT *
                FROM unified_customers
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for customer in customers:

            headers = {
                "Authorization": (
                    f"token {erp.api_key}:{erp.api_secret}"
                ),
                "Content-Type": "application/json"
            }

            # CHECK IF CUSTOMER EXISTS
            check_url = (
                f"{erp.erp_url}/api/resource/Customer/"
                f"{customer.customer_name}"
            )

            check_response = requests.get(
                check_url,
                headers=headers
            )

            if check_response.status_code == 200:

                results.append(
                    {
                        "customer_name":
                            customer.customer_name,
                        "status":
                            "Skipped - Already Exists"
                    }
                )

                continue

            url = (
                f"{erp.erp_url}/api/resource/Customer"
            )

            payload = build_payload_from_mapping(
                customer,
                target_mappings.get(
                    "Customer",
                    {}
                )
            )

            payload["customer_type"] = "Company"

            response = requests.post(
                url,
                json=payload,
                headers=headers
            )

            if response.status_code in [200, 201]:

                print(
                    "CUSTOMER DATA:",
                    customer.customer_name,
                    customer.contact_name,
                    customer.email,
                    customer.phone,
                    customer.address
                )

                contact_payload = build_payload_from_mapping(
                    customer,
                    target_mappings.get(
                        "Contact",
                        {}
                    )
                )

                if (
                    "first_name" not in contact_payload
                    and customer.customer_name
                ):
                    contact_payload[
                        "first_name"
                    ] = customer.customer_name

                if customer.email:

                    contact_payload[
                        "email_ids"
                    ] = [
                        {
                            "email_id":
                                customer.email,
                            "is_primary":
                                1
                        }
                    ]

                if customer.phone:

                    contact_payload[
                        "phone_nos"
                    ] = [
                        {
                            "phone":
                                customer.phone,

                            "is_primary_phone":
                                1,

                            "is_primary_mobile_no":
                                0
                        }
                    ]

                contact_payload[
                    "links"
                ] = [
                    {
                        "link_doctype":
                            "Customer",

                        "link_name":
                            customer.customer_name
                    }
                ]

                contact_response = requests.post(
                    f"{erp.erp_url}/api/resource/Contact",
                    json=contact_payload,
                    headers=headers
                )

                print(
                    "CONTACT:",
                    customer.customer_name,
                    contact_response.status_code,
                    contact_response.json()
                )

                print(
                    "ADDRESS DEBUG:",
                    customer.customer_name,
                    repr(customer.address)
                )

                address_payload = build_payload_from_mapping(
                    customer,
                    target_mappings.get(
                        "Address",
                        {}
                    )
                )

                address_parts = (
                    customer.address.split(",")
                    if customer.address
                    else []
                )

                if (
                    "state" not in address_payload
                    and len(address_parts) > 2
                ):
                    address_payload["state"] = (
                        address_parts[2].strip()
                    )

                if (
                    "country" not in address_payload
                    and len(address_parts) > 3
                ):
                    address_payload["country"] = (
                        address_parts[3].strip()
                    )

                if (
                    "city" not in address_payload
                    and len(address_parts) > 1
                ):
                    address_payload["city"] = (
                        address_parts[1].strip()
                    )

                address_payload[
                    "address_title"
                ] = customer.customer_name

                address_payload[
                    "address_type"
                ] = "Billing"

                address_payload[
                    "links"
                ] = [
                    {
                        "link_doctype":
                            "Customer",

                        "link_name":
                            customer.customer_name
                    }
                ]

                print(
                    "POSTAL TO ERP:",
                    customer.customer_name,
                    customer.postal_code
                )

                print(
                    "ADDRESS PAYLOAD:",
                    address_payload
                )

                address_response = requests.post(
                    f"{erp.erp_url}/api/resource/Address",
                    json=address_payload,
                    headers=headers
                )

                print("ADDRESS PAYLOAD:")
                print(address_payload)

                print("ADDRESS STATUS:")
                print(address_response.status_code)

                print("ADDRESS RESPONSE:")
                print(address_response.text)

                contact_name = (
                    contact_response.json()
                    .get("data", {})
                    .get("name")
                )

                address_name = (
                    address_response.json()
                    .get("data", {})
                    .get("name")
                )

                customer_update = {
                    "customer_primary_contact": contact_name,
                    "customer_primary_address": address_name
                }

                requests.put(
                    f"{erp.erp_url}/api/resource/Customer/{customer.customer_name}",
                    json=customer_update,
                    headers=headers
                )

            results.append(
                {
                    "customer_name":
                        customer.customer_name,
                    "status_code":
                        response.status_code,
                    "response":
                        response.json()
                }
            )

        return results
    finally:
        db.close()