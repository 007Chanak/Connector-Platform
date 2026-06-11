import requests
from sqlalchemy import text
from app.database import SessionLocal

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


def sync_erpnext_suppliers_service(
    user_id,
    tenant_id
):

    db = SessionLocal()
    try:

        suppliers = (
            fetch_complete_erpnext_suppliers(
                user_id,
                tenant_id
            )
        )

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

        for supplier in suppliers:

            existing = db.execute(
                text("""
                    SELECT id
                    FROM unified_suppliers
                    WHERE
                        tenant_id = :tenant_id
                        AND supplier_name = :supplier_name
                        AND source = 'erpnext'
                """),
                {
                    "tenant_id": tenant_id,
                    "supplier_name":
                        supplier["supplier_name"]
                }
            ).fetchone()

            print(
                "EXISTING CHECK:",
                supplier["supplier_name"],
                existing
            )

            if existing:
                continue

            print(
                "INSERTING:",
                supplier
            )

            db.execute(
                text("""
                    INSERT INTO unified_suppliers
                    (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        supplier_name,
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
                        :supplier_name,
                        :contact_name,
                        :email,
                        :phone,
                        :address,
                        :postal_code
                    )
                """),
                {
                    "user_id": user_id,

                    "tenant_id": tenant_id,

                    "source": "erpnext",

                    "external_id":
                        supplier["supplier_name"],

                    "supplier_name":
                        supplier["supplier_name"],

                    "contact_name":
                        supplier["contact_name"],

                    "email":
                        supplier["email"],

                    "phone":
                        supplier["phone"],

                    "address":
                        supplier["address"],

                    "postal_code":
                        supplier["postal_code"]
                }
            )

            synced.append(
                supplier
            )

        db.commit()

        return {
            "message":
                "ERPNext suppliers synced successfully",

            "total_synced":
                len(synced),

            "suppliers":
                synced
        }

    finally:
        db.close()