import requests
from sqlalchemy import text
from app.database import SessionLocal
from app.services.xero_auth_service import (
    refresh_xero_token
)


def fetch_xero_sales_orders(
    access_token,
    tenant_id
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

    return response.json().get(
        "Quotes",
        []
    )


def sync_xero_sales_orders_service(
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

        sales_orders = (
            fetch_xero_sales_orders(
                integration.access_token,
                integration.tenant_id
            )
        )

        inserted = 0

        for quote in sales_orders:

            if quote.get("Status") == "DELETED":
                continue

            for item in quote.get(
                "LineItems",
                []
            ):

                existing_so = db.execute(
                    text("""
                        SELECT id
                        FROM unified_sales_orders
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
                            quote.get(
                                "QuoteNumber"
                            ),

                        "item_code":
                            item.get(
                                "ItemCode"
                            )
                    }
                ).fetchone()

                if existing_so:
                    continue

                item_row = db.execute(
                    text("""
                        SELECT item_name
                        FROM unified_items
                        WHERE
                            tenant_id = :tenant_id
                            AND item_code = :item_code
                        LIMIT 1
                    """),
                    {
                        "tenant_id": tenant_id,
                        "item_code": item.get("ItemCode")
                    }
                ).fetchone()

                print(
                    "QUOTE:",
                    quote.get(
                        "QuoteNumber"
                    ),
                    quote.get(
                        "Contact",
                        {}
                    ).get(
                        "Name"
                    ),
                    quote.get(
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
                            "xero",

                        "external_id":
                            quote.get(
                                "QuoteID"
                            ),

                        "canonical_key":
                            quote.get(
                                "QuoteNumber"
                            ),

                        "so_number":
                            quote.get(
                                "QuoteNumber"
                            ),

                        "customer_name":
                            quote.get(
                                "Contact",
                                {}
                            ).get(
                                "Name"
                            ),

                        "order_date":
                            quote.get(
                                "DateString",
                                ""
                            )[:10],

                        "delivery_date":
                            quote.get(
                                "ExpiryDateString",
                                ""
                            )[:10],

                        "item_code":
                            item.get(
                                "ItemCode"
                            ),

                        "item_name":
                            item_row.item_name
                            if item_row
                            else item.get(
                                "ItemCode"
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
                            quote.get(
                                "Total"
                            ),

                        "status":
                            quote.get(
                                "Status"
                            )
                    }
                )

                inserted += 1

        db.commit()

        return {
            "message":
                "Xero Sales Orders synced successfully",

            "inserted":
                inserted
        }

    finally:
        db.close()