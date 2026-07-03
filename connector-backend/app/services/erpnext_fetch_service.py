import requests
from sqlalchemy import text
from app.database import SessionLocal

from app.services.mapping_service import (
    build_payload_from_mapping,
    get_target_mappings
)

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

def fetch_complete_erpnext_suppliers(user_id,tenant_id):

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

        suppliers_response = requests.get(
            f"{erp.erp_url}/api/resource/Supplier",
            headers=headers
        )

        suppliers = suppliers_response.json().get(
            "data",
            []
        )

        unified_suppliers = []

        for supplier in suppliers:

            supplier_name = supplier.get("name")
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
                    supplier_name,
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
                        == "Supplier"
                        and
                        link.get("link_name")
                        == supplier_name
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
                            supplier_name,
                            "Email:",
                            email,
                            "Phone:",
                            phone
                        )

                        break

                if contact_person:
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
                        == "Supplier"
                        and
                        link.get("link_name")
                        == supplier_name
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
                            supplier_name,
                            postal_code
                        )

                        break

                if address:
                    break

            supplier_data = {
                "supplier_name": supplier_name,
                "contact_name": contact_person,
                "email": email,
                "phone": phone,
                "address": address,
                "postal_code": postal_code
            }

            print("CONTACT PERSON:", contact_person)

            print(
                "APPENDING:",
                supplier_data
            )

            unified_suppliers.append(
                supplier_data
            )

        return unified_suppliers
    finally:
        db.close()

def fetch_erpnext_complete_items(user_id,tenant_id):

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

        items_url = (
            f"{erp.erp_url}/api/resource/Item"
        )

        items_response = requests.get(
            items_url,
            headers=headers
        )

        items = items_response.json().get(
            "data",
            []
        )

        complete_items = []

        for item in items:

            item_name = item.get("name")

            item_doc = requests.get(
                f"{erp.erp_url}/api/resource/Item/{item_name}",
                headers=headers
            ).json()["data"]

            complete_items.append(
                item_doc
            )

        return complete_items
    finally:
        db.close()

def fetch_complete_erpnext_sales_orders(
    erp_url,
    api_key,
    api_secret
):

    headers = {
        "Authorization":
            f"token {api_key}:{api_secret}"
    }

    sales_orders_url = (
        f"{erp_url}/api/resource/Sales Order"
    )

    sales_orders = requests.get(
        sales_orders_url,
        headers=headers
    ).json().get(
        "data",
        []
    )

    complete_sales_orders = []

    for so in sales_orders:

        so_name = so["name"]

        so_response = requests.get(
            f"{erp_url}/api/resource/Sales Order/{so_name}",
            headers=headers
        )

        if so_response.status_code == 200:

            complete_sales_orders.append(
                so_response.json()["data"]
            )

    return complete_sales_orders