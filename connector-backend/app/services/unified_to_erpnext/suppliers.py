import requests
from sqlalchemy import text
from app.database import SessionLocal

def push_suppliers_to_erpnext(user_id, tenant_id):

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

        suppliers = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'xero'
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for supplier in suppliers:

            headers = {
                "Authorization": (
                    f"token {erp.api_key}:{erp.api_secret}"
                ),
                "Content-Type": "application/json"
            }

            # CHECK IF CUSTOMER EXISTS
            check_url = (
                f"{erp.erp_url}/api/resource/Supplier/"
                f"{supplier.supplier_name}"
            )

            check_response = requests.get(
                check_url,
                headers=headers
            )

            if check_response.status_code == 200:

                results.append(
                    {
                        "supplier_name":
                            supplier.supplier_name,
                        "status":
                            "Skipped - Already Exists"
                    }
                )

                continue

            url = (
                f"{erp.erp_url}/api/resource/Supplier"
            )

            address_parts = (
                supplier.address.split(",")
                if supplier.address
                else []
            )

            country = (
                address_parts[-1].strip()
                if len(address_parts) > 0
                else "India"
            )


            payload = {
                "supplier_name":
                    supplier.supplier_name,

                "supplier_group":
                    "Services",

                "supplier_type":
                    "Company",

                "country": 
                    country
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers
            )

            if response.status_code in [200, 201]:

                print(
                    "CUSTOMER DATA:",
                    supplier.supplier_name,
                    supplier.contact_name,
                    supplier.email,
                    supplier.phone,
                    supplier.address
                )

                contact_payload = {
                    "first_name": (
                        supplier.contact_name.split(" ")[0]
                        if supplier.contact_name
                        else supplier.supplier_name
                    ),

                    "last_name": (
                        " ".join(supplier.contact_name.split(" ")[1:])
                        if supplier.contact_name
                        and len(supplier.contact_name.split(" ")) > 1
                        else ""
                    ),

                    "email_ids": [
                        {
                            "email_id": supplier.email,
                            "is_primary": 1
                        }
                    ] if supplier.email else [],

                    "phone_nos": [
                        {
                            "phone": supplier.phone,
                            "is_primary_phone": 1,
                            "is_primary_mobile_no": 0
                        }
                    ] if supplier.phone else [],

                    "links": [
                        {
                            "link_doctype": "Supplier",
                            "link_name": supplier.supplier_name
                        }
                    ]
                }

                contact_response = requests.post(
                    f"{erp.erp_url}/api/resource/Contact",
                    json=contact_payload,
                    headers=headers
                )

                print(
                    "CONTACT:",
                    supplier.supplier_name,
                    contact_response.status_code,
                    contact_response.json()
                )

                print(
                    "ADDRESS DEBUG:",
                    supplier.supplier_name,
                    repr(supplier.address)
                )

                address_parts = (
                    supplier.address.split(",")
                    if supplier.address
                    else []
                )

                address_payload = {
                    "address_title": supplier.supplier_name,

                    "address_type": "Billing",

                    "address_line1":
                        address_parts[0].strip()
                        if len(address_parts) > 0
                        else "",

                    "city":
                        address_parts[1].strip()
                        if len(address_parts) > 1
                        else "",

                    "state":
                        address_parts[-2].strip()
                        if len(address_parts) > 1
                        else "Tamil Nadu",

                    "country":
                        address_parts[-1].strip()
                        if len(address_parts) > 0
                        else "India",
                    
                    "pincode":
                        supplier.postal_code or "",

                    "links": [
                        {
                            "link_doctype": "Supplier",
                            "link_name": supplier.supplier_name
                        }
                    ]
                }

                print(
                    "POSTAL TO ERP:",
                    supplier.supplier_name,
                    supplier.postal_code
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

                print(
                    "ADDRESS RESPONSE:",
                    address_response.status_code,
                    address_response.json()
                )

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

            results.append(
                {
                    "supplier_name":
                        supplier.supplier_name,
                    "status_code":
                        response.status_code,
                    "response":
                        response.json()
                }
            )

        return results
    finally:
        db.close()