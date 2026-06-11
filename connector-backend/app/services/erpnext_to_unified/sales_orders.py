import requests
from sqlalchemy import text
from app.database import SessionLocal


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


def sync_erpnext_sales_orders_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        if not erp:
            return {
                "error":
                    "No ERPNext integration found"
            }

        sales_orders = (
            fetch_complete_erpnext_sales_orders(
                erp.erp_url,
                erp.api_key,
                erp.api_secret
            )
        )

        inserted = 0

        for so in sales_orders:

            for item in so.get(
                "items",
                []
            ):

                existing_so = db.execute(
                    text("""
                        SELECT id
                        FROM unified_sales_orders
                        WHERE
                            tenant_id = :tenant_id
                            AND source = 'erpnext'
                            AND canonical_key = :canonical_key
                            AND item_code = :item_code
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "canonical_key":
                            so["name"],

                        "item_code":
                            item["item_code"]
                    }
                ).fetchone()

                if existing_so:
                    continue

                print(
                    "SO:",
                    so["name"],
                    so.get("customer_name"),
                    so.get("grand_total")
                )

                print(
                    "ITEM:",
                    item.get("item_code"),
                    item.get("item_name"),
                    item.get("qty"),
                    item.get("rate")
                )

                db.execute(
                    text("""
                        INSERT INTO
                        unified_sales_orders
                        (
                            tenant_id,
                            user_id,
                            source,
                            external_id,
                            canonical_key,
                            so_number,
                            customer_name,
                            order_date,
                            delivery_date,
                            item_code,
                            item_name,
                            quantity,
                            unit_price,
                            line_amount,
                            total_amount,
                            status
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source,
                            :external_id,
                            :canonical_key,
                            :so_number,
                            :customer_name,
                            :order_date,
                            :delivery_date,
                            :item_code,
                            :item_name,
                            :quantity,
                            :unit_price,
                            :line_amount,
                            :total_amount,
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
                            so["name"],

                        "canonical_key":
                            so["name"],

                        "so_number":
                            so["name"],

                        "customer_name":
                            so.get(
                                "customer_name"
                            ),

                        "order_date":
                            so.get(
                                "transaction_date"
                            ),

                        "delivery_date":
                            so.get(
                                "delivery_date"
                            ),

                        "item_code":
                            item.get(
                                "item_code"
                            ),

                        "item_name":
                            item.get(
                                "item_name"
                            ),

                        "quantity":
                            item.get(
                                "qty"
                            ),

                        "unit_price":
                            item.get(
                                "rate"
                            ),

                        "line_amount":
                            item.get(
                                "amount"
                            ),

                        "total_amount":
                            so.get(
                                "grand_total"
                            ),

                        "status":
                            so.get(
                                "status"
                            )
                    }
                )

                inserted += 1

        db.commit()

        return {
            "message":
                "Sales Orders synced successfully",

            "inserted":
                inserted
        }

    finally:
        db.close()