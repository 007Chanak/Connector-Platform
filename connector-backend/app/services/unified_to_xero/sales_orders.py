import requests
from sqlalchemy import text
from app.database import SessionLocal


def get_xero_contact_id(
    access_token,
    tenant_id,
    customer_name
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
            customer_name.strip().lower()
        ):

            return contact.get(
                "ContactID"
            )

    return None


def push_sales_order_to_xero(
    access_token,
    tenant_id,
    so_number,
    app_tenant_id
):

    db = SessionLocal()

    try:

        so_rows = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
                WHERE
                    tenant_id = :tenant_id
                    AND so_number = :so_number
                ORDER BY id
            """),
            {
                "tenant_id":
                    app_tenant_id,

                "so_number":
                    so_number
            }
        ).fetchall()

        if not so_rows:

            return {
                "status_code": 404,
                "response": {
                    "error":
                        "Sales Order not found"
                }
            }

        first_so = so_rows[0]

        line_items = []

        for row in so_rows:

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
            first_so.customer_name
        )

        if not contact_id:

            return {
                "status_code": 400,
                "response": {
                    "error":
                        f"Customer not found in Xero: {first_so.customer_name}"
                }
            }

        payload = {
            "Quotes": [
                {
                    "QuoteNumber":
                        first_so.so_number,

                    "Title":
                        first_so.so_number,

                    "Contact": {
                        "ContactID":
                            contact_id
                    },

                    "Date":
                        str(first_so.order_date),

                    "ExpiryDate":
                        str(first_so.delivery_date),

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
            "XERO SO PAYLOAD:",
            payload
        )

        response = requests.post(
            "https://api.xero.com/api.xro/2.0/Quotes",
            headers=headers,
            json=payload
        )

        try:
            response_json = response.json()
        except Exception:
            response_json = response.text

        print(
            "XERO SO RESPONSE:",
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


def sales_order_exists_in_xero(
    access_token,
    tenant_id,
    so_number
):

    response = requests.get(
        "https://api.xero.com/api.xro/2.0/Quotes",
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

    quotes = response.json().get(
        "Quotes",
        []
    )

    for quote in quotes:

        quote_number = (
            quote.get(
                "QuoteNumber",
                ""
            ).strip().lower()
        )

        status = (
            quote.get(
                "Status",
                ""
            ).upper()
        )

        if (
            quote_number
            ==
            so_number.strip().lower()
            and
            status != "DELETED"
        ):
            return True

    return False


def push_unified_sales_orders_to_xero(
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
                "user_id":
                    user_id
            }
        ).scalar()

        sales_orders = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
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

        processed_sos = set()

        for so in sales_orders:

            if so.so_number in processed_sos:
                continue

            processed_sos.add(
                so.so_number
            )

            existing_migration = db.execute(
                text("""
                    SELECT id
                    FROM migration_logs
                    WHERE
                        tenant_id = :tenant_id
                        AND source_system = 'erpnext'
                        AND target_system = 'xero'
                        AND source_invoice_number = :so_number
                """),
                {
                    "tenant_id":
                        app_tenant_id,

                    "so_number":
                        so.so_number
                }
            ).fetchone()

            if existing_migration:

                exists_in_xero = (
                    sales_order_exists_in_xero(
                        access_token,
                        tenant_id,
                        so.so_number
                    )
                )

                if exists_in_xero:

                    results.append(
                        {
                            "so_number":
                                so.so_number,

                            "status":
                                "Skipped - Already Migrated"
                        }
                    )

                    continue

            response = (
                push_sales_order_to_xero(
                    access_token,
                    tenant_id,
                    so.so_number,
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
                            so.so_number
                    }
                )

                db.commit()

            results.append(
                {
                    "so_number":
                        so.so_number,

                    "status_code":
                        response["status_code"],

                    "response":
                        response["response"]
                }
            )

        return results

    finally:
        db.close()