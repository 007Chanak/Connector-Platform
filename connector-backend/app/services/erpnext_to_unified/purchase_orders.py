import requests
from sqlalchemy import text
from app.database import SessionLocal



def fetch_complete_erpnext_purchase_orders(
    erp_url,
    api_key,
    api_secret
):

    headers = {
        "Authorization":
            f"token {api_key}:{api_secret}"
    }

    purchase_orders_url = (
        f"{erp_url}/api/resource/Purchase Order"
    )

    purchase_orders = requests.get(
        purchase_orders_url,
        headers=headers
    ).json().get(
        "data",
        []
    )

    complete_purchase_orders = []

    for po in purchase_orders:

        po_name = po["name"]

        po_response = requests.get(
            f"{erp_url}/api/resource/Purchase Order/{po_name}",
            headers=headers
        )

        if po_response.status_code == 200:

            complete_purchase_orders.append(
                po_response.json()["data"]
            )

    return complete_purchase_orders


def sync_erpnext_purchase_orders_service(
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

        purchase_orders = (
            fetch_complete_erpnext_purchase_orders(
                erp.erp_url,
                erp.api_key,
                erp.api_secret
            )
        )

        inserted = 0

        for po in purchase_orders:

            for item in po.get(
                "items",
                []
            ):

                existing_po = db.execute(
                    text("""
                        SELECT id
                        FROM unified_purchase_orders
                        WHERE
                            tenant_id = :tenant_id
                            AND source = 'erpnext'
                            AND canonical_key = :canonical_key
                            AND item_code = :item_code
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "canonical_key": po["name"],

                        "item_code":
                            item["item_code"]
                    }
                ).fetchone()

                if existing_po:
                    continue

                print(
                    "PO:",
                    po["name"],
                    po.get("supplier_name"),
                    po.get("grand_total")
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
                        unified_purchase_orders
                        (
                            tenant_id,
                            user_id,
                            source,
                            external_id,
                            canonical_key,
                            po_number,
                            supplier_name,
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
                            :po_number,
                            :supplier_name,
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
                            po["name"],

                        "canonical_key":
                            po["name"],

                        "po_number":
                            po["name"],

                        "supplier_name":
                            po.get(
                                "supplier_name"
                            ),

                        "order_date":
                            po.get(
                                "transaction_date"
                            ),

                        "delivery_date":
                            po.get(
                                "schedule_date"
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
                            po.get(
                                "grand_total"
                            ),

                        "status":
                            po.get(
                                "status"
                            )
                    }
                )

                inserted += 1

        db.commit()

        return {
            "message":
                "Purchase Orders synced successfully",

            "inserted":
                inserted
        }

    finally:
        db.close()