from sqlalchemy import text

from app.database import SessionLocal

from app.services.xero_fetch_service import (
    fetch_complete_xero_bills
)

from app.services.mapping_service import (
    get_mapping_dict
)

from app.services.xero_to_unified.transformer import (
    transform_bill_using_mapping,
    transform_bill_item_using_mapping
)


def sync_xero_bills_service(
    user_id,
    tenant_id
):

    db = SessionLocal()

    try:

        bills = (
            fetch_complete_xero_bills(
                user_id,
                tenant_id
            )
        )

        bill_mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="bills",
            source_system="xero"
        )

        bill_item_mapping = get_mapping_dict(
            tenant_id=tenant_id,
            entity_type="bill_items",
            source_system="xero"
        )

        print("BILL MAPPING:")
        print(bill_mapping)

        print("BILL ITEM MAPPING:")
        print(bill_item_mapping)

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

        for bill in bills:

            transformed_bill = (
                transform_bill_using_mapping(
                    bill,
                    bill_mapping
                )
            )

            print(
                "BILL DATA:",
                transformed_bill
            )

            existing_bill = db.execute(
                text("""
                    SELECT id
                    FROM unified_bills
                    WHERE
                        tenant_id = :tenant_id
                        AND external_id = :external_id
                        AND source = 'xero'
                """),
                {
                    "tenant_id": tenant_id,
                    "external_id":
                        transformed_bill[
                            "external_id"
                        ]
                }
            ).fetchone()

            if existing_bill:
                continue

            db.execute(
                text("""
                    INSERT INTO unified_bills
                    (
                        tenant_id,
                        user_id,
                        source,
                        external_id,
                        bill_number,
                        supplier_name,
                        bill_date,
                        due_date,
                        total_amount,
                        tax_amount,
                        status,
                        created_at,
                        subtotal
                    )
                    VALUES
                    (
                        :tenant_id,
                        :user_id,
                        :source,
                        :external_id,
                        :bill_number,
                        :supplier_name,
                        :bill_date,
                        :due_date,
                        :total_amount,
                        :tax_amount,
                        :status,
                        NOW(),
                        :subtotal
                    )
                """),
                {
                    "user_id": user_id,

                    "tenant_id": tenant_id,

                    "source": "xero",

                    "external_id":
                        transformed_bill.get(
                            "external_id"
                        ),

                    "bill_number":
                        transformed_bill.get(
                            "bill_number"
                        ),

                    "supplier_name":
                        transformed_bill.get(
                            "supplier_name"
                        ),

                    "bill_date":
                        transformed_bill.get(
                            "bill_date"
                        ),

                    "due_date":
                        transformed_bill.get(
                            "due_date"
                        ),

                    "total_amount":
                        transformed_bill.get(
                            "total_amount"
                        ),

                    "tax_amount":
                        transformed_bill.get(
                            "tax_amount"
                        ),

                    "status":
                        transformed_bill.get(
                            "status"
                        ),

                    "subtotal":
                        transformed_bill.get(
                            "subtotal"
                        )
                }
            )

            print(
                "BILL:",
                bill.get(
                    "InvoiceNumber"
                )
            )

            print(
                "LINE ITEMS COUNT:",
                len(
                    bill.get(
                        "LineItems",
                        []
                    )
                )
            )

            for line_item in bill.get(
                "LineItems",
                []
            ):

                transformed_item = (
                    transform_bill_item_using_mapping(
                        line_item,
                        transformed_bill.get(
                            "external_id"
                        ),
                        bill_item_mapping
                    )
                )

                print(
                    "BILL ITEM:",
                    transformed_item
                )

                existing_item = db.execute(
                    text("""
                        SELECT id
                        FROM unified_bill_items
                        WHERE
                            tenant_id = :tenant_id
                            AND bill_external_id = :bill_external_id
                            AND item_external_id = :item_external_id
                            AND source = 'xero'
                    """),
                    {
                        "tenant_id":
                            tenant_id,

                        "bill_external_id":
                            transformed_item.get(
                                "bill_external_id"
                            ),

                        "item_external_id":
                            transformed_item.get(
                                "item_external_id"
                            )
                    }
                ).fetchone()

                if existing_item:
                    continue

                db.execute(
                    text("""
                        INSERT INTO unified_bill_items
                        (
                            tenant_id,
                            user_id,
                            source,
                            bill_external_id,
                            item_external_id,
                            item_code,
                            item_name,
                            quantity,
                            unit_price,
                            line_total
                        )
                        VALUES
                        (
                            :tenant_id,
                            :user_id,
                            :source,
                            :bill_external_id,
                            :item_external_id,
                            :item_code,
                            :item_name,
                            :quantity,
                            :unit_price,
                            :line_total
                        )
                    """),
                    {
                        "user_id":
                            user_id,

                        "tenant_id":
                            tenant_id,

                        "source":
                            "xero",

                        "bill_external_id":
                            transformed_item.get(
                                "bill_external_id"
                            ),

                        "item_external_id":
                            transformed_item.get(
                                "item_external_id"
                            ),

                        "item_code":
                            transformed_item.get(
                                "item_code"
                            ),

                        "item_name":
                            transformed_item.get(
                                "item_name"
                            ),

                        "quantity":
                            transformed_item.get(
                                "quantity"
                            ),

                        "unit_price":
                            transformed_item.get(
                                "unit_price"
                            ),

                        "line_total":
                            transformed_item.get(
                                "line_total"
                            )
                    }
                )

            synced.append(
                transformed_bill
            )

        db.commit()

        return {
            "message":
                "Bills synced successfully",

            "total_synced":
                len(synced),

            "bills":
                synced
        }

    finally:
        db.close()