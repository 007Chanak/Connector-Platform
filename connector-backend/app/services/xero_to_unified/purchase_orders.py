import requests
from sqlalchemy import text
from app.database import SessionLocal
from app.services.xero_auth_service import (
    refresh_xero_token
)

def fetch_xero_purchase_orders(
    access_token,
    tenant_id
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

    return response.json().get(
        "PurchaseOrders",
        []
    )

def sync_xero_purchase_orders_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    provider = 'xero'
                    AND tenant_id_fk = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    tenant_id
            }
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        refresh_xero_token(
            integration.id
        )

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE id = :id
            """),
            {
                "id":
                    integration.id
            }
        ).fetchone()

        purchase_orders = (
            fetch_xero_purchase_orders(
                integration.access_token,
                integration.tenant_id
            )
        )

        inserted = 0

        for po in purchase_orders:

            if po.get("Status") == "DELETED":
                continue

            for item in po.get(
                "LineItems",
                []
            ):

                existing_po = db.execute(
                    text("""
                        SELECT id
                        FROM unified_purchase_orders
                        WHERE
                            tenant_id = :tenant_id
                            AND source = 'xero'
                            AND canonical_key = :canonical_key
                            AND item_code = :item_code
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "canonical_key":
                            po.get(
                                "PurchaseOrderNumber"
                            ),

                        "item_code":
                            item.get(
                                "ItemCode"
                            )
                    }
                ).fetchone()

                if existing_po:
                    continue

                print(
                    "PO:",
                    po.get(
                        "PurchaseOrderNumber"
                    ),
                    po.get(
                        "Contact",
                        {}
                    ).get(
                        "Name"
                    ),
                    po.get(
                        "Total"
                    )
                )

                print(
                    "ITEM:",
                    item.get(
                        "ItemCode"
                    ),
                    item.get(
                        "Description"
                    ),
                    item.get(
                        "Quantity"
                    ),
                    item.get(
                        "UnitAmount"
                    )
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
                            "xero",

                        "external_id":
                            po.get(
                                "PurchaseOrderID"
                            ),

                        "canonical_key":
                            po.get(
                                "PurchaseOrderNumber"
                            ),

                        "po_number":
                            po.get(
                                "PurchaseOrderNumber"
                            ),

                        "supplier_name":
                            po.get(
                                "Contact",
                                {}
                            ).get(
                                "Name"
                            ),

                        "order_date":
                            po.get(
                                "DateString",
                                ""
                            )[:10],

                        "delivery_date":
                            po.get(
                                "DeliveryDateString",
                                ""
                            )[:10],

                        "item_code":
                            item.get(
                                "ItemCode"
                            ),

                        "item_name":
                            item.get(
                                "Description"
                            ),

                        "quantity":
                            item.get(
                                "Quantity"
                            ),

                        "unit_price":
                            item.get(
                                "UnitAmount"
                            ),

                        "line_amount":
                            item.get(
                                "LineAmount"
                            ),

                        "total_amount":
                            po.get(
                                "Total"
                            ),

                        "status":
                            po.get(
                                "Status"
                            )
                    }
                )

                inserted += 1

        db.commit()

        return {
            "message":
                "Xero Purchase Orders synced successfully",

            "inserted":
                inserted
        }

    finally:
        db.close()