import requests
from sqlalchemy import text
from app.database import SessionLocal


def push_purchase_order_to_xero(
    access_token,
    tenant_id,
    po_number,
    app_tenant_id
):

    db = SessionLocal()

    try:

        po_rows = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                WHERE
                    tenant_id = :tenant_id
                    AND po_number = :po_number
                ORDER BY id
            """),
            {
                "tenant_id": app_tenant_id,
                "po_number": po_number
            }
        ).fetchall()

        if not po_rows:

            return {
                "status_code": 404,
                "response": {
                    "error": "Purchase Order not found"
                }
            }

        first_po = po_rows[0]

        line_items = []

        for row in po_rows:

            line_items.append(
                {
                    "ItemCode":
                        row.item_code,

                    "Description":
                        row.item_name,

                    "Quantity":
                        float(row.quantity)
                        if row.quantity
                        else 1,

                    "UnitAmount":
                        float(row.unit_price)
                        if row.unit_price
                        else 0
                }
            )

        contact_id = get_xero_contact_id(
            access_token,
            tenant_id,
            first_po.supplier_name
        )

        if not contact_id:

            return {
                "status_code": 400,
                "response": {
                    "error":
                        f"Supplier not found in Xero: {first_po.supplier_name}"
                }
            }

        payload = {
            "PurchaseOrders": [
                {
                    "PurchaseOrderNumber":
                        first_po.po_number,
                    
                    "Reference": first_po.po_number,

                    "Contact": {
                        "ContactID":
                            contact_id
                    },

                    "Date":
                        str(first_po.order_date),

                    "DeliveryDate":
                        str(first_po.delivery_date),

                    "Status":
                        "DRAFT",

                    "LineItems":
                        line_items
                }
            ]
        }

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                tenant_id,

            "Accept":
                "application/json",

            "Content-Type":
                "application/json"
        }

        print(
            "XERO PO PAYLOAD:",
            payload
        )

        response = requests.post(
            "https://api.xero.com/api.xro/2.0/PurchaseOrders",
            headers=headers,
            json=payload
        )

        try:
            response_json = response.json()
        except Exception:
            response_json = response.text

        print(
            "XERO PO RESPONSE:",
            response_json
        )

        return {
            "status_code":
                response.status_code,

            "response":
                response_json
        }

    finally:
        db.close()

def purchase_order_exists_in_xero(
    access_token,
    tenant_id,
    po_number
):

    response = requests.get(
        "https://api.xero.com/api.xro/2.0/PurchaseOrders",
        headers={
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                tenant_id,

            "Accept":
                "application/json"
        }
    )

    if response.status_code != 200:
        return False

    purchase_orders = response.json().get(
        "PurchaseOrders",
        []
    )

    for po in purchase_orders:

        purchase_order_number = (
            po.get(
                "PurchaseOrderNumber",
                ""
            ).strip().lower()
        )

        status = (
            po.get(
                "Status",
                ""
            ).upper()
        )

        print(
            "CHECK:",
            purchase_order_number,
            status,
            purchase_order_number
            ==
            po_number.strip().lower()
        )

        if (
            purchase_order_number
            ==
            po_number.strip().lower()
            and
            status != "DELETED"
        ):
            return True

    return False

def push_unified_purchase_orders_to_xero(
    access_token,
    tenant_id,
    user_id,
    integration_id
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

        purchase_orders = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                WHERE
                    tenant_id = :tenant_id
                    AND source = 'erpnext'
            """),
            {
                "tenant_id":
                    app_tenant_id
            }
        ).fetchall()

        results = []

        processed_pos = set()

        for po in purchase_orders:

            if po.po_number in processed_pos:
                continue

            processed_pos.add(
                po.po_number
            )

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :po_number
                """),
                {
                    "tenant_id":
                        app_tenant_id,

                    "po_number":
                        po.po_number
                }
            ).fetchone()

            print(
                "EXISTING MIGRATION:",
                existing_migration
            )

            if existing_migration:

                exists_in_xero = (
                    purchase_order_exists_in_xero(
                        access_token,
                        tenant_id,
                        po.po_number
                    )
                )

                print(
                    "EXISTS IN XERO:",
                    exists_in_xero
                )

                print(
                    "CURRENT PO:",
                    po.po_number
                )

                if exists_in_xero:

                    print(
                        "SKIPPING:",
                        po.po_number
                    )

                    results.append(
                        {
                            "po_number":
                                po.po_number,

                            "status":
                                "Skipped - Already Migrated"
                        }
                    )

                    continue

            response = (
                push_purchase_order_to_xero(
                    access_token,
                    tenant_id,
                    po.po_number,
                    app_tenant_id
                )
            )

            if response["status_code"] in [200, 201]:

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
                            po.po_number
                    }
                )

                db.commit()

            results.append(
                {
                    "po_number":
                        po.po_number,

                    "status_code":
                        response["status_code"],

                    "response":
                        response["response"]
                }
            )

        return results

    finally:
        db.close()

def get_xero_contact_id(
    access_token,
    tenant_id,
    supplier_name
):

    response = requests.get(
        "https://api.xero.com/api.xro/2.0/Contacts",
        headers={
            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                tenant_id,

            "Accept":
                "application/json"
        }
    )

    if response.status_code != 200:
        return None

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
            supplier_name.strip().lower()
        ):

            return contact.get(
                "ContactID"
            )

    return None