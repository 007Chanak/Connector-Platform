from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import text
from app.database import SessionLocal
from pydantic import BaseModel
from typing import Any, Dict

class MappingSaveRequest(BaseModel):
    mappings: Dict[str, Any]

class WorkflowSaveRequest(BaseModel):

    mappings: Dict[str, Any]
    disabled: Dict[str, Any]

from app.dependencies.auth import (
    get_current_user
)
from app.services.erpnext_metadata_service import (
    get_erpnext_doctype_fields
)
from app.services.mapping_service import (
    generate_mapping,
    get_table_columns,
    save_mapping,
    get_mapping,
    generate_target_mapping,
    generate_xero_target_mapping,
    save_target_mapping,
    generate_target_doctypes,
    save_entity_targets,
    get_complete_mapping
)
from app.services.xero_fetch_service import (
    fetch_complete_xero_customers,
    fetch_complete_xero_suppliers,
    fetch_complete_xero_items,
    fetch_complete_xero_invoices,
    fetch_complete_xero_bills,
    fetch_complete_xero_sales_orders,
    fetch_complete_xero_purchase_orders,
    fetch_complete_xero_accounts,
    
)

from app.services.erpnext_to_unified.sales_orders import (
    fetch_complete_erpnext_sales_orders
)

router = APIRouter(
    tags=["Mapping Xero"]
)

def get_xero_item_fields():

    return [

        "Code",
        "Name",
        "Description",

        "SalesUnitPrice",

        "PurchaseUnitPrice",

        "IsSold",

        "IsPurchased"
    ]

@router.post(
    "/target-discovery/test/items/xero"
)
def test_item_xero_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        return {

            "entity_type":
                "items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                [
                    {
                        "target_doctype":
                            "Item",
                        "confidence":
                            1.0
                    }
                ]
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/items/xero"
)
def save_item_xero_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "items",

        target_system=
            "xero",

        targets=
            [
                {
                    "target_doctype":
                        "Item",
                    "confidence":
                        1.0
                }
            ]
    )

    return {

        "message":
            "Xero item targets saved"
    }


@router.post(
    "/target-mapping/generate/items/xero"
)
def generate_item_xero_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        target_fields = [

            "Code",
            "Name",
            "Description",
            "SalesUnitPrice",
            "PurchaseUnitPrice",
            "IsSold",
            "IsPurchased"
        ]

        mapping = generate_xero_target_mapping(

            entity_type=
                "items",

            unified_fields=
                unified_fields,

            target_fields=
                target_fields,

            sample_record=
                dict(sample_item)
        )

        return {

            "sample_item":
                dict(sample_item),

            "unified_fields":
                unified_fields,

            "mapping":
                mapping,

            "target_fields":
                target_fields
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/items/xero"
)
def save_item_xero_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_item_xero_target_mapping(
            current_user
        )
    )

    mappings = {
        "Item": {
            "mapping":
                generated["mapping"]
        }
    }

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "items",

        target_system=
            "xero",

        mappings=
            mappings
    )

    return {

        "message":
            "Xero item mappings saved"
    }

@router.post(
    "/mapping/preview/items/xero"
)
def preview_xero_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    return get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "items",

        source_system=
            "erpnext",

        target_system=
            "xero"
    )

@router.post(
    "/workflow/save/items/xero"
)
def save_xero_item_workflow(

    payload: WorkflowSaveRequest,

    current_user=Depends(
        get_current_user
    )

):

    source_mapping = {}

    for source_field, unified_field in (
        payload
        .mappings
        ["source_to_unified"]
        .items()
    ):

        if payload.disabled.get(
            "source",
            {}
        ).get(
            source_field,
            False
        ):
            continue

        source_mapping[
            source_field
        ] = unified_field

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "erpnext_items",

        source_system=
            "erpnext",

        mapping=
            source_mapping
    )

    target_mappings = {}

    for doctype, config in (
        payload
        .mappings
        ["unified_to_target"]
        .items()
    ):

        target_mappings[
            doctype
        ] = {
            "mapping": {}
        }

        for unified_field, target_field in (
            config[
                "mapping"
            ].items()
        ):

            key = (
                f"{doctype}:"
                f"{unified_field}"
            )

            if payload.disabled.get(
                "target",
                {}
            ).get(
                key,
                False
            ):
                continue

            target_mappings[
                doctype
            ][
                "mapping"
            ][
                unified_field
            ] = target_field

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "items",

        target_system=
            "xero",

        mappings=
            target_mappings
    )

    return {

        "message":
            "Xero Item workflow saved successfully"
    }

@router.post(
    "/source-mapping/generate/sales-orders"
)
def generate_sales_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchone()

        sample_orders = (
            fetch_complete_erpnext_sales_orders(
                integration.erp_url,
                integration.api_key,
                integration.api_secret
            )
        )

        if not sample_orders:

            return {
                "error":
                    "No sales orders found"
            }

        sample_order = sample_orders[0]

        source_fields = [

            "name",
            "customer",
            "transaction_date",
            "delivery_date",
            "grand_total",
            "status"
        ]

        destination_fields = [

            "external_id",
            "so_number",
            "customer_name",
            "order_date",
            "delivery_date",
            "total_amount",
            "status"
        ]

        mapping = generate_mapping(
            entity_type=
                "erpnext-sales_orders",

            source_fields=
                source_fields,

            destination_fields=
                destination_fields,

            sample_record=
                sample_order
        )

        return {

            "sample_sales_order":
                sample_order,

            "source_fields":
                source_fields,

            "destination_fields":
                destination_fields,

            "mapping":
                mapping
        }

    finally:

        db.close()

@router.post(
    "/source-mapping/save/sales-orders"
)
def save_sales_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_sales_order_mapping(
            current_user
        )
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "erpenxt-sales_orders",

        source_system=
            "erpnext",

        mapping=
            generated["mapping"]
    )

    return {

        "message":
            "Sales Order mapping saved"
    }

@router.post(
    "/source-mapping/generate/sales-order-items"
)
def generate_sales_order_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchone()

        sales_orders = (
            fetch_complete_erpnext_sales_orders(
                integration.erp_url,
                integration.api_key,
                integration.api_secret
            )
        )

        if not sales_orders:

            return {
                "error":
                    "No Sales Orders Found"
            }

        sample_item = sales_orders[0]["items"][0]

        source_fields = [

            "parent",
            "item_code",
            "item_name",
            "qty",
            "rate",
            "amount"
        ]

        destination_fields = [

            "so_external_id",
            "item_code",
            "item_name",
            "quantity",
            "unit_price",
            "line_total"
        ]

        mapping = generate_mapping(

            entity_type=
                "erpnext_sales_order_items",

            source_fields=
                source_fields,

            destination_fields=
                destination_fields,

            sample_record=
                sample_item
        )

        return {

            "sample_item":
                sample_item,

            "source_fields":
                source_fields,

            "destination_fields":
                destination_fields,

            "mapping":
                mapping
        }

    finally:

        db.close()

@router.post(
    "/source-mapping/save/sales-order-items"
)
def save_sales_order_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_sales_order_item_mapping(
            current_user
        )
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "erpnext_sales_order_items",

        source_system=
            "erpnext",

        mapping=
            generated["mapping"]
    )

    return {

        "message":
            "Sales Order Item Mapping Saved"
    }

@router.post(
    "/target-discovery/test/sales-orders/xero"
)
def test_sales_order_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_so = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        unified_fields = [

            field

            for field in sample_so.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        targets = [

            {
                "target_doctype":
                    "Quote",

                "confidence":
                    1.0
            }
        ]

        return {

            "entity_type":
                "sales_orders",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/sales-orders/xero"
)
def save_sales_order_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_sales_order_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_orders",

        target_system=
            "xero",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Sales Order targets saved"
    }

@router.post(
    "/target-mapping/generate/sales-orders/xero"
)
def generate_sales_order_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_so = db.execute(
            text("""
                SELECT *
                FROM unified_sales_orders
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        unified_fields = [

            field

            for field in sample_so.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        target_fields = [

            "QuoteNumber",
            "ContactID",
            "Date",
            "ExpiryDate",
            "Total",
            "Status"
        ]

        mapping = (
            generate_xero_target_mapping(

                entity_type=
                    "sales_orders",

                unified_fields=
                    unified_fields,

                target_fields=
                    target_fields,

                sample_record=
                    dict(sample_so)
            )
        )

        return {

            "sample_sales_order":
                dict(sample_so),

            "unified_fields":
                unified_fields,

            "target_fields":
                target_fields,

            "mapping":
                mapping
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/sales-orders/xero"
)
def save_sales_order_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_sales_order_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_orders",

        target_system=
            "xero",

        mappings={
            "Quote": {
                "mapping":
                    generated["mapping"]
            }
        }
    )

    return {

        "message":
            "Sales Order target mapping saved"
    }

@router.post(
    "/mapping/preview/sales-orders/xero"
)
def preview_sales_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    return get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_orders",

        source_system=
            "erpnext",

        target_system=
            "xero"
    )

