import requests

from sqlalchemy import text

from app.database import SessionLocal



def fetch_erpnext_customers(user_id,tenant_id):

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

        url = f"{erp.erp_url}/api/resource/Customer"

        headers = {
            "Authorization": (
                f"token {erp.api_key}:{erp.api_secret}"
            )
        }

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()
    finally:
        db.close()


def fetch_complete_erpnext_customers(user_id,tenant_id):

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
            return []

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        customers_response = requests.get(
            f"{erp.erp_url}/api/resource/Customer",
            headers=headers
        )

        customers = customers_response.json().get(
            "data",
            []
        )

        unified_customers = []

        for customer in customers:

            customer_name = customer.get("name")
            contact_person = ""

            email = ""
            phone = ""
            address = ""
            postal_code = ""

            # CONTACT LOOKUP
            contacts_response = requests.get(
                f"{erp.erp_url}/api/resource/Contact",
                headers=headers
            )

            contacts = contacts_response.json().get(
                "data",
                []
            )

            for contact in contacts:

                contact_name = contact.get("name")

                print(
                    "Checking",
                    customer_name,
                    "against contact",
                    contact_name
                )

                contact_doc = requests.get(
                    f"{erp.erp_url}/api/resource/Contact/{contact_name}",
                    headers=headers
                ).json()["data"]

                for link in contact_doc.get(
                    "links",
                    []
                ):

                    if (
                        link.get("link_doctype")
                        == "Customer"
                        and
                        link.get("link_name")
                        == customer_name
                    ):
                        print(contact_doc)

                        contact_person = contact_doc.get(
                            "full_name",
                            ""
                        )

                        email = contact_doc.get(
                            "email_id",
                            ""
                        )

                        phone = (
                            contact_doc.get(
                                "mobile_no"
                            )
                            or
                            contact_doc.get(
                                "phone"
                            )
                            or
                            ""
                        )

                        print(
                            "MATCHED:",
                            customer_name,
                            "Email:",
                            email,
                            "Phone:",
                            phone
                        )

                        break

            # ADDRESS LOOKUP
            addresses_response = requests.get(
                f"{erp.erp_url}/api/resource/Address",
                headers=headers
            )

            addresses = addresses_response.json().get(
                "data",
                []
            )

            for addr in addresses:

                addr_name = addr.get("name")

                addr_doc = requests.get(
                    f"{erp.erp_url}/api/resource/Address/{addr_name}",
                    headers=headers
                ).json()["data"]

                for link in addr_doc.get(
                    "links",
                    []
                ):

                    if (
                        link.get("link_doctype")
                        == "Customer"
                        and
                        link.get("link_name")
                        == customer_name
                    ):

                        address = ", ".join(
                            filter(
                                None,
                                [
                                    addr_doc.get(
                                        "address_line1"
                                    ),
                                    addr_doc.get(
                                        "city"
                                    ),
                                    addr_doc.get(
                                        "state"
                                    ),
                                    addr_doc.get(
                                        "country"
                                    )
                                ]
                            )
                        )

                        postal_code = (
                            addr_doc.get("pincode")
                            or ""
                        )

                        print(
                            "POSTAL:",
                            customer_name,
                            postal_code
                        )

                        break

            customer_data = {
                "customer_name": customer_name,
                "contact_name": contact_person,
                "email": email,
                "phone": phone,
                "address": address,
                "postal_code": postal_code
            }

            print("CONTACT PERSON:", contact_person)

            print(
                "APPENDING:",
                customer_data
            )

            unified_customers.append(
                customer_data
            )

        return unified_customers
    finally:
        db.close()


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

            payload = {
                "customer_name":
                    customer.customer_name,
                "customer_type":
                    "Company"
            }

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

                contact_payload = {
                    "first_name": (
                        customer.contact_name.split(" ")[0]
                        if customer.contact_name
                        else customer.customer_name
                    ),

                    "last_name": (
                        " ".join(customer.contact_name.split(" ")[1:])
                        if customer.contact_name
                        and len(customer.contact_name.split(" ")) > 1
                        else ""
                    ),

                    "email_ids": [
                        {
                            "email_id": customer.email,
                            "is_primary": 1
                        }
                    ] if customer.email else [],

                    "phone_nos": [
                        {
                            "phone": customer.phone,
                            "is_primary_phone": 1,
                            "is_primary_mobile_no": 0
                        }
                    ] if customer.phone else [],

                    "links": [
                        {
                            "link_doctype": "Customer",
                            "link_name": customer.customer_name
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
                    customer.customer_name,
                    contact_response.status_code,
                    contact_response.json()
                )

                print(
                    "ADDRESS DEBUG:",
                    customer.customer_name,
                    repr(customer.address)
                )

                address_parts = (
                    customer.address.split(",")
                    if customer.address
                    else []
                )

                address_payload = {
                    "address_title": customer.customer_name,

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
                        address_parts[2].strip()
                        if len(address_parts) > 2
                        else "Tamil Nadu",

                    "country":
                        address_parts[3].strip()
                        if len(address_parts) > 3
                        else "India",
                    
                    "pincode":
                        customer.postal_code or "",

                    "links": [
                        {
                            "link_doctype": "Customer",
                            "link_name": customer.customer_name
                        }
                    ]
                }

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

def fetch_erpnext_sales_invoices(user_id,tenant_id):

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
            return []

        headers = {
            "Authorization": (
                f"token {erp.api_key}:{erp.api_secret}"
            )
        }

        invoices_url = (
            f"{erp.erp_url}/api/resource/Sales Invoice"
        )

        invoices_response = requests.get(
            invoices_url,
            headers=headers
        )

        invoices = invoices_response.json().get(
            "data",
            []
        )

        complete_invoices = []

        for invoice in invoices:

            invoice_name = invoice.get("name")

            invoice_doc = requests.get(
                f"{erp.erp_url}/api/resource/Sales Invoice/{invoice_name}",
                headers=headers
            ).json()["data"]

            complete_invoices.append(
                invoice_doc
            )

        return complete_invoices
    finally:
        db.close()

def push_invoices_to_erpnext(user_id,tenant_id):

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

        invoices = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE tenant_id = :tenant_id
            """),
            {
                "tenant_id": tenant_id,
            }
        ).fetchall()

        results = []

        for invoice in invoices:

            url = (
                f"{erp.erp_url}/api/resource/Sales Invoice"
            )

            headers = {
                "Authorization": (
                    f"token {erp.api_key}:{erp.api_secret}"
                ),
                "Content-Type": "application/json"
            }

            payload = {
                "customer": invoice.customer_name,
                "posting_date": str(
                    invoice.invoice_date
                ),
                "due_date": str(
                    invoice.due_date
                ),
                "items": [
                    {
                        "item_code": "TEST-001",
                        "qty": 1,
                        "rate": float(
                            invoice.total_amount
                        )
                    }
                ]
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers
            )

            results.append(
                {
                    "invoice_number":
                        invoice.invoice_number,
                    "status_code":
                        response.status_code,
                    "response":
                        response.json()
                }
            )

        return results
    finally:
        db.close()

