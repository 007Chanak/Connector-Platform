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
    fetch_complete_xero_accounts
)

router = APIRouter(
    tags=["AI Mapping"]
)


@router.post(
    "/mapping/generate/customers"
)
def generate_customer_mapping(
    current_user=Depends(
        get_current_user
    )
):

    customers = (
        fetch_complete_xero_customers(
            current_user.id,
            current_user.tenant_id
        )
    )

    print(
        "TOTAL CUSTOMERS:",
        len(customers)
    )

    print(
        "FIRST CUSTOMER:",
        customers[0]
    )

    all_fields = set()

    for customer in customers:

        all_fields.update(
            customer.keys()
        )

    source_fields = list(
        all_fields
    )

    all_destination_fields = (
        get_table_columns(
            "unified_customers"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",

            "user_id",

            "tenant_id",

            "created_at",

            "updated_at",

            "source"

        }

    ]

    mapping = generate_mapping(
        "customers",
        source_fields,
        destination_fields,
        customers[0]
    )

    return {

        "sample_customer":
            customers[0],

        "source_fields":
            source_fields,

        "destination_fields":
            destination_fields,

        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/customers"
)
def save_generated_customer_mapping(
    current_user=Depends(
        get_current_user
    )
):

    customers = (
        fetch_complete_xero_customers(
            current_user.id,
            current_user.tenant_id
        )
    )

    all_fields = set()

    for customer in customers:

        all_fields.update(
            customer.keys()
        )

    source_fields = list(
        all_fields
    )

    all_destination_fields = (
        get_table_columns(
            "unified_customers"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "user_id",
            "tenant_id",
            "created_at",
            "updated_at",
            "source"
        }
    ]

    mapping = generate_mapping(
        "customers",
        source_fields,
        destination_fields,
        customers[0]
    )

    return save_mapping(
    tenant_id=current_user.tenant_id,
    entity_type="customers",
    source_system="xero",
    mapping=mapping
)

@router.get(
    "/mapping/customers"
)
def view_customer_mapping(
    current_user=Depends(
        get_current_user
    )

):
    return get_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="customers",
        source_system="xero"
    )

@router.post(
    "/mapping/generate/suppliers"
)
def generate_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):

    suppliers = (
        fetch_complete_xero_suppliers(
            current_user.id,
            current_user.tenant_id
        )
    )

    all_fields = set()

    for supplier in suppliers:

        all_fields.update(
            supplier.keys()
        )

    source_fields = list(
        all_fields
    )

    all_destination_fields = (
        get_table_columns(
            "unified_suppliers"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "user_id",
            "tenant_id",
            "created_at",
            "updated_at",
            "source"

        }

    ]

    mapping = generate_mapping(

        "suppliers",

        source_fields,

        destination_fields,

        suppliers[0]

    )

    return {

        "sample_supplier":
            suppliers[0],

        "source_fields":
            source_fields,

        "destination_fields":
            destination_fields,

        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/suppliers"
)
def save_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):
    suppliers = (
        fetch_complete_xero_suppliers(
            current_user.id,
            current_user.tenant_id
        )
    )


    all_fields = set()

    for supplier in suppliers:

        all_fields.update(
            supplier.keys()
        )

    source_fields = list(
        all_fields
    )

    all_destination_fields = (
        get_table_columns(
            "unified_suppliers"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "user_id",
            "tenant_id",
            "created_at",
            "updated_at",
            "source"

        }

    ]

    mapping = generate_mapping(
        "suppliers",
        source_fields,
        destination_fields,
        suppliers[0]
    )

    save_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="suppliers",
        source_system="xero",
        mapping=mapping
    )

    return mapping

@router.get(
    "/mapping/suppliers"
)
def get_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):

    return get_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="suppliers",
        source_system="xero"
    )

@router.post(
    "/mapping/generate/items"
)
def generate_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    items = (
        fetch_complete_xero_items(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not items:
        return {
            "error": "No items found"
        }

    sample_item = items[0]

    source_fields = [

        "ItemID",
        "Code",
        "Name",
        "Description",
        "PurchaseDescription",
        "SalesDetails.UnitPrice",
        "PurchaseDetails.UnitPrice",
        "IsTrackedAsInventory",
        "IsSold",
        "IsPurchased"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_items"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "user_id",
            "tenant_id",
            "source",
            "created_at",
            "updated_at"
        }
    ]
    sample_item = items[0]

    mapping = generate_mapping(
        "items",
        source_fields,
        destination_fields,
        sample_item,
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

@router.post(
    "/mapping/save/items"
)
def save_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = generate_item_mapping(
        current_user
    )

    mapping = generated["mapping"]

    save_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="items",
        source_system="xero",
        mapping=mapping
    )

    return {
        "message":
            "Item mappings saved",
        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/invoices"
)
def generate_invoice_mapping(

    current_user=Depends(
        get_current_user
    )

):

    invoices = (
        fetch_complete_xero_invoices(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not invoices:

        return {
            "error": "No invoices found"
        }

    sample_invoice = invoices[0]

    source_fields = [
        "InvoiceID",
        "InvoiceNumber",
        "Contact.Name",
        "Date",
        "DueDate",
        "SubTotal",
        "TotalTax",
        "Total",
        "CurrencyCode",
        "Status"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_invoices"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "user_id",
            "tenant_id",
            "source",
            "created_at",
            "origin_system"
        }
    ]

    mapping = generate_mapping(
        "invoices",
        source_fields,
        destination_fields,
        sample_invoice
    )

    return {
        "sample_invoice":
            sample_invoice,
        "source_fields":
            source_fields,
        "destination_fields":
            destination_fields,
        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/invoices"
)
def save_invoice_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_invoice_mapping(
            current_user
        )
    )

    save_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="invoices",
        source_system="xero",
        mapping=generated[
            "mapping"
        ]
    )

    return {
        "message":
            "Invoice mappings saved",
        "mapping":
            generated[
                "mapping"
            ]
    }

@router.post(
    "/mapping/generate/invoice-items"
)
def generate_invoice_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    invoices = (
        fetch_complete_xero_invoices(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not invoices:
        return {
            "error": "No invoices found"
        }

    sample_invoice = invoices[0]

    if not sample_invoice.get(
        "LineItems"
    ):
        return {
            "error": "No invoice items found"
        }

    sample_item = (
        sample_invoice["LineItems"][0]
    )

    source_fields = [

        "Item.ItemID",
        "ItemCode",
        "Description",
        "Quantity",
        "UnitAmount",
        "LineAmount"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_invoice_items"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "tenant_id",
            "user_id",
            "source",

            # Parent invoice field
            "invoice_external_id"
        }
    ]

    mapping = generate_mapping(

        "invoice_items",

        source_fields,

        destination_fields,

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

@router.post(
    "/mapping/save/invoice-items"
)
def save_invoice_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_invoice_item_mapping(
            current_user
        )
    )

    mapping = generated[
        "mapping"
    ]

    print(mapping)

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        source_system=
            "xero",

        mapping=
            mapping
    )

    return {

        "message":
            "Invoice item mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/bills"
)
def generate_bill_mapping(

    current_user=Depends(
        get_current_user
    )

):

    bills = (
        fetch_complete_xero_bills(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not bills:

        return {
            "error": "No bills found"
        }

    sample_bill = bills[0]

    source_fields = [
        "InvoiceID",
        "InvoiceNumber",
        "Contact.Name",
        "Date",
        "DueDate",
        "SubTotal",
        "TotalTax",
        "Total",
        "Status"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_bills"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "user_id",
            "tenant_id",
            "source",
            "created_at"
        }
    ]

    mapping = generate_mapping(
        "bills",
        source_fields,
        destination_fields,
        sample_bill
    )

    return {
        "sample_bill":
            sample_bill,
        "source_fields":
            source_fields,
        "destination_fields":
            destination_fields,
        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/bills"
)
def save_bill_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_bill_mapping(
            current_user
        )
    )

    save_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="bills",
        source_system="xero",
        mapping=generated[
            "mapping"
        ]
    )

    return {
        "message":
            "Bill mappings saved",
        "mapping":
            generated[
                "mapping"
            ]
    }

@router.post(
    "/mapping/generate/bill-items"
)
def generate_bill_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    bills = (
        fetch_complete_xero_bills(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not bills:
        return {
            "error": "No bills found"
        }

    sample_bill = bills[0]

    if not sample_bill.get(
        "LineItems"
    ):
        return {
            "error": "No bill items found"
        }

    sample_item = (
        sample_bill["LineItems"][0]
    )

    source_fields = [

        "Item.ItemID",
        "ItemCode",
        "Description",
        "Quantity",
        "UnitAmount",
        "LineAmount"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_bill_items"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "tenant_id",
            "user_id",
            "source",

            # SYSTEM FIELD
            # Comes from parent bill
            # Never AI mapped
            "bill_external_id"
        }
    ]

    mapping = generate_mapping(

        "bill_items",

        source_fields,

        destination_fields,

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

@router.post(
    "/mapping/save/bill-items"
)
def save_bill_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_bill_item_mapping(
            current_user
        )
    )

    mapping = generated[
        "mapping"
    ]

    print(mapping)

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        source_system=
            "xero",

        mapping=
            mapping
    )

    return {

        "message":
            "Bill item mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/sales-orders"
)
def generate_sales_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    sales_orders = (
        fetch_complete_xero_sales_orders(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not sales_orders:

        return {
            "error":
                "No sales orders found"
        }

    sample_so = sales_orders[0]

    source_fields = [
        "QuoteID",
        "QuoteNumber",
        "Contact.Name",
        "Date",
        "ExpiryDate",
        "Total",
        "Status"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_sales_orders"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "tenant_id",
            "user_id",
            "source",
            "created_at",
            "canonical_key"
        }
    ]

    mapping = generate_mapping(
        "sales_orders",
        source_fields,
        destination_fields,
        sample_so
    )

    return {
        "sample_sales_order":
            sample_so,
        "source_fields":
            source_fields,
        "destination_fields":
            destination_fields,
        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/sales-orders"
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
        tenant_id=current_user.tenant_id,
        entity_type="sales_orders",
        source_system="xero",
        mapping=generated[
            "mapping"
        ]
    )

    return {
        "message":
            "Sales order mapping saved",
        "mapping":
            generated[
                "mapping"
            ]
    }

@router.post(
    "/mapping/generate/sales-order-items"
)
def generate_sales_order_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    sales = (
        fetch_complete_xero_sales_orders(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not sales:
        return {
            "error": "No sales order found"
        }

    sample_sale = sales[0]

    if not sample_sale.get(
        "LineItems"
    ):
        return {
            "error": "No sales order items found"
        }

    sample_item = (
        sample_sale["LineItems"][0]
    )

    source_fields = [

        "LineItemID",
        "ItemCode",
        "Description",
        "Quantity",
        "UnitAmount",
        "LineAmount"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_sales_order_items"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "tenant_id",
            "user_id",
            "source",
            "so_external_id"
        }
    ]

    mapping = generate_mapping(

        "sales_order_items",

        source_fields,

        destination_fields,

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


@router.post(
    "/mapping/save/sales-order-items"
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

    mapping = generated[
        "mapping"
    ]

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        source_system=
            "xero",

        mapping=
            mapping
    )

    return {

        "message":
            "Sales Order Item mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/purchase-orders"
)
def generate_purchase_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    purchase_orders = (
        fetch_complete_xero_purchase_orders(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not purchase_orders:

        return {
            "error":
                "No purchase orders found"
        }

    sample_purchase_order = (
        purchase_orders[0]
    )

    source_fields = [
        "PurchaseOrderID",
        "PurchaseOrderNumber",
        "Contact.Name",
        "Date",
        "DeliveryDate",
        "Total",
        "Status"
    ]

    destination_fields = [
        "external_id",
        "po_number",
        "supplier_name",
        "order_date",
        "delivery_date",
        "total_amount",
        "status"
    ]

    mapping = generate_mapping(
        "purchase_orders",
        source_fields,
        destination_fields,
        sample_purchase_order
    )

    return {
        "sample_purchase_order":
            sample_purchase_order,
        "source_fields":
            source_fields,
        "destination_fields":
            destination_fields,
        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/purchase-orders"
)
def save_purchase_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_purchase_order_mapping(
            current_user
        )
    )

    save_mapping(
        tenant_id=
            current_user.tenant_id,
        entity_type=
            "purchase_orders",
        source_system=
            "xero",
        mapping=
            generated["mapping"]
    )

    return {
        "message":
            "Purchase Order mappings saved",
        "mapping":
            generated["mapping"]
    }

@router.post(
    "/mapping/generate/purchase-order-items"
)
def generate_purchase_order_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    purchase_orders = (
        fetch_complete_xero_purchase_orders(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not purchase_orders:

        return {
            "error":
                "No purchase orders found"
        }

    sample_po = purchase_orders[0]

    if not sample_po.get(
        "LineItems"
    ):

        return {
            "error":
                "No purchase order items found"
        }

    sample_item = (
        sample_po["LineItems"][0]
    )

    source_fields = [

        "Item.ItemID",
        "ItemCode",
        "Description",
        "Quantity",
        "UnitAmount",
        "LineAmount"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_purchase_order_items"
        )
    )

    destination_fields = [

        field

        for field in all_destination_fields

        if field not in {

            "id",
            "tenant_id",
            "user_id",
            "source",

            "po_external_id"
        }
    ]

    mapping = generate_mapping(

        "purchase_order_items",

        source_fields,

        destination_fields,

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

@router.post(
    "/mapping/save/purchase-order-items"
)
def save_purchase_order_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_purchase_order_item_mapping(
            current_user
        )
    )

    mapping = generated[
        "mapping"
    ]

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        source_system=
            "xero",

        mapping=
            mapping
    )

    return {

        "message":
            "Purchase Order Item mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/accounts"
)
def generate_account_mapping(

    current_user=Depends(
        get_current_user
    )

):

    accounts = (
        fetch_complete_xero_accounts(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not accounts:

        return {
            "error": "No accounts found"
        }

    sample_account = accounts[0]

    source_fields = [
        "AccountID",
        "Code",
        "Name",
        "Type",
        "Class",
        "Description",
        "Status"
    ]

    all_destination_fields = (
        get_table_columns(
            "unified_accounts"
        )
    )

    destination_fields = [
        field
        for field in all_destination_fields
        if field not in {
            "id",
            "tenant_id",
            "source",
            "created_at",
            "canonical_key",
            "raw_data",
            "company",
            "currency",
            "parent_account",
            "is_group"
        }
    ]

    mapping = generate_mapping(
        "accounts",
        source_fields,
        destination_fields,
        sample_account
    )

    return {
        "sample_account":
            sample_account,
        "source_fields":
            source_fields,
        "destination_fields":
            destination_fields,
        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/accounts"
)
def save_account_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_account_mapping(
            current_user
        )
    )

    save_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="accounts",
        source_system="xero",
        mapping=generated[
            "mapping"
        ]
    )

    return {
        "message":
            "Account mappings saved",
        "mapping":
            generated[
                "mapping"
            ]
    }

@router.post(
    "/target-mapping/generate/customers"
)
def generate_customer_target_mapping(

    current_user=Depends(
        get_current_user
    )

):
    db = SessionLocal()

    try:
        sample_customer = db.execute(
            text("""
                SELECT *
                FROM unified_customers
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_customer:
            return {
                "error":
                    "No customers found"
            }

        unified_fields = [

            field

            for field in sample_customer.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'customers'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type="customers",
                    target_doctype=
                        target_doctype,
                    unified_fields=
                        unified_fields,
                    target_fields=
                        target_fields,
                    sample_record=
                        dict(
                            sample_customer
                        )
                )
            )

            mappings[
                target_doctype
            ] = {
                "target_fields":
                    target_fields,
                "mapping":
                    mapping
            }

        return {
            "sample_customer":
                dict(
                    sample_customer
                ),
            "unified_fields":
                unified_fields,
            "mappings":
                mappings
        }

    finally:
        db.close()

@router.post(
    "/target-mapping/save/customers"
)
def save_customer_target_mapping(
    current_user=Depends(
        get_current_user
    )
):

    generated = generate_customer_target_mapping(
        current_user
    )

    save_target_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="customers",
        target_system="erpnext",
        mappings=generated["mappings"]
    )

    return {
        "message": "Customer mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/suppliers"
)
def generate_supplier_target_mapping(

    current_user=Depends(
        get_current_user
    )

):
    db = SessionLocal()

    try:

        sample_supplier = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_supplier:

            return {
                "error":
                    "No suppliers found"
            }

        unified_fields = [

            field

            for field in sample_supplier.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'suppliers'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type="suppliers",
                    target_doctype=
                        target_doctype,
                    unified_fields=
                        unified_fields,
                    target_fields=
                        target_fields,
                    sample_record=
                        dict(
                            sample_supplier
                        )
                )
            )

            mappings[
                target_doctype
            ] = {
                "target_fields":
                    target_fields,
                "mapping":
                    mapping
            }

        return {

            "sample_supplier":
                dict(
                    sample_supplier
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()


@router.post(
    "/target-mapping/save/suppliers"
)
def save_supplier_target_mapping(
    current_user=Depends(
        get_current_user
    )
):

    generated = generate_supplier_target_mapping(
        current_user
    )

    save_target_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="suppliers",
        target_system="erpnext",
        mappings=generated["mappings"]
    )

    return {
        "message": "Supplier mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/items"
)
def generate_item_target_mapping(

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

        if not sample_item:
            return {
                "error":
                    "No items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'items'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type="items",
                    target_doctype=
                        target_doctype,
                    unified_fields=
                        unified_fields,
                    target_fields=
                        target_fields,
                    sample_record=
                        dict(
                            sample_item
                        )
                )
            )

            mappings[
                target_doctype
            ] = {
                "target_fields":
                    target_fields,
                "mapping":
                    mapping
            }

        return {
            "sample_customer":
                dict(
                    sample_item
                ),
            "unified_fields":
                unified_fields,
            "mappings":
                mappings
        }

    finally:
        db.close()

@router.post(
    "/target-mapping/save/items"
)
def save_item_target_mapping(
    current_user=Depends(
        get_current_user
    )
):

    generated = generate_item_target_mapping(
        current_user
    )

    save_target_mapping(
        tenant_id=current_user.tenant_id,
        entity_type="items",
        target_system="erpnext",
        mappings=generated["mappings"]
    )

    return {
        "message": "Item mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/bills"
)
def generate_bill_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_bill = db.execute(
            text("""
                SELECT *
                FROM unified_bills
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_bill:
            return {
                "error":
                    "No bills found"
            }

        unified_fields = [

            field

            for field in sample_bill.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'bills'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type="bills",
                    target_doctype=
                        target_doctype,
                    unified_fields=
                        unified_fields,
                    target_fields=
                        target_fields,
                    sample_record=
                        dict(
                            sample_bill
                        )
                )
            )

            mappings[
                target_doctype
            ] = {
                "target_fields":
                    target_fields,
                "mapping":
                    mapping
            }

        return {

            "sample_bill":
                dict(
                    sample_bill
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/bills"
)
def save_bill_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_bill_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bills",

        target_system=
            "erpnext",

        mappings=
            generated["mappings"]
    )

    return {

        "message":
            "Bill mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/bill-items"
)
def generate_bill_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_bill_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No bill items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'bill_items'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "bill_items",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_item
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_item":
                dict(
                    sample_item
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/bill-items"
)
def save_bill_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_bill_item_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Bill Item mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/invoices"
)
def generate_invoice_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_invoice = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_invoice:

            return {
                "error":
                    "No invoices found"
            }

        unified_fields = [

            field

            for field in sample_invoice.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "origin_system"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'invoices'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "Sales Invoices",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_invoice
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_invoice":
                dict(
                    sample_invoice
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/invoices"
)
def save_invoice_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_invoice_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoices",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Invoice mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/invoice-items"
)
def generate_invoice_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_invoice_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No invoice items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'invoice_items'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "Sales Invoice Items",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_item
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_item":
                dict(
                    sample_item
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/invoice-items"
)
def save_invoice_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_invoice_item_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Invoice Item mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/purchase-orders"
)
def generate_purchase_order_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_po = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_po:

            return {
                "error":
                    "No purchase orders found"
            }

        unified_fields = [

            field

            for field in sample_po.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'purchase_orders'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "purchase_orders",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_po
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_purchase_order":
                dict(
                    sample_po
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/purchase-orders"
)
def save_purchase_order_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_purchase_order_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_orders",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Purchase Order mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/purchase-order-items"
)
def generate_purchase_order_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_order_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No purchase order items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'purchase_order_items'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "purchase_order_items",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_item
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_item":
                dict(
                    sample_item
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/purchase-order-items"
)
def save_purchase_order_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_purchase_order_item_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Purchase Order Item mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/sales-orders"
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

        if not sample_so:

            return {
                "error":
                    "No sales orders found"
            }

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

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'sales_orders'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "sales_orders",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_so
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_sales_order":
                dict(
                    sample_so
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/sales-orders"
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
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Sales Order mappings generated and saved"
    }

@router.post(
    "/target-mapping/generate/sales-order-items"
)
def generate_sales_order_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_sales_order_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No sales order items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        targets = db.execute(
            text("""
                SELECT
                    target_doctype
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = 'sales_order_items'
                    AND target_system = 'erpnext'
                ORDER BY confidence DESC
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchall()

        mappings = {}

        for target in targets:

            target_doctype = (
                target.target_doctype
            )

            target_fields = (
                get_erpnext_doctype_fields(
                    current_user.tenant_id,
                    target_doctype
                )
            )

            mapping = (
                generate_target_mapping(
                    entity_type=
                        "sales_order_items",

                    target_doctype=
                        target_doctype,

                    unified_fields=
                        unified_fields,

                    target_fields=
                        target_fields,

                    sample_record=
                        dict(
                            sample_item
                        )
                )
            )

            mappings[
                target_doctype
            ] = {

                "target_fields":
                    target_fields,

                "mapping":
                    mapping
            }

        return {

            "sample_item":
                dict(
                    sample_item
                ),

            "unified_fields":
                unified_fields,

            "mappings":
                mappings
        }

    finally:

        db.close()

@router.post(
    "/target-mapping/save/sales-order-items"
)
def save_sales_order_item_target_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_sales_order_item_target_mapping(
            current_user
        )
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        target_system=
            "erpnext",

        mappings=
            generated[
                "mappings"
            ]
    )

    return {

        "message":
            "Sales Order Item mappings generated and saved"
    }

@router.post(
    "/target-discovery/test/customers"
)
def test_customer_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_customer = db.execute(
            text("""
                SELECT *
                FROM unified_customers
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

            for field in sample_customer.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        available_doctypes = [

            "Customer",
            "Supplier",

            "Contact",
            "Address",

            "Item",

            "Sales Invoice",
            "Purchase Invoice",

            "Sales Order",
            "Purchase Order"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="customers",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "customers",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/customers"
)
def save_customer_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_customer_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "customers",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Customer target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/suppliers"
)
def test_supplier_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_supplier = db.execute(
            text("""
                SELECT *
                FROM unified_suppliers
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_supplier:

            return {
                "error":
                    "No suppliers found"
            }

        unified_fields = [

            field

            for field in sample_supplier.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        available_doctypes = [

            "Customer",
            "Supplier",

            "Contact",
            "Address",

            "Item",

            "Sales Invoice",
            "Purchase Invoice",

            "Sales Order",
            "Purchase Order"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="suppliers",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "suppliers",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/suppliers"
)
def save_supplier_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_supplier_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "suppliers",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Supplier target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/items"
)
def test_item_target_discovery(

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

        available_doctypes = [

            "Item",

            "Item Group",

            "UOM",

            "Customer",
            "Supplier",

            "Sales Invoice",
            "Purchase Invoice"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="items",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/items"
)
def save_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_item_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "items",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Item targets saved successfully"
    }

@router.post(
    "/target-discovery/test/bills"
)
def test_bill_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_bill = db.execute(
            text("""
                SELECT *
                FROM unified_bills
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

            for field in sample_bill.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at"
            }
        ]

        available_doctypes = [

            "Customer",
            "Supplier",

            "Contact",
            "Address",

            "Item",

            "Sales Invoice",
            "Purchase Invoice",

            "Sales Order",
            "Purchase Order"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="bills",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "bills",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:
        db.close()

@router.post(
    "/target-discovery/save/bills"
)
def save_bill_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_bill_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bills",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Bill target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/bill-items"
)
def test_bill_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_bill_items
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
                "source"
            }
        ]

        available_doctypes = [

            "Purchase Invoice Item"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="bill_items",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "bill_items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/bill-items"
)
def save_bill_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_bill_item_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Bill Item target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/invoices"
)
def test_invoice_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_invoice = db.execute(
            text("""
                SELECT *
                FROM unified_invoices
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

            for field in sample_invoice.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "origin_system"
            }
        ]

        available_doctypes = [

            "Sales Invoice",
            "Customer",
            "Contact",
            "Address"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="invoices",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "invoices",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/invoices"
)
def save_invoice_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_invoice_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoices",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Invoice target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/invoice-items"
)
def test_invoice_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_invoice_items
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
                "source"
            }
        ]

        available_doctypes = [

            "Sales Invoice Item"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="invoice_items",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "invoice_items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/invoice-items"
)
def save_invoice_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_invoice_item_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Invoice Item target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/purchase-orders"
)
def test_purchase_order_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_po = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_orders
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_po:

            return {
                "error":
                    "No purchase orders found"
            }

        unified_fields = [

            field

            for field in sample_po.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source",
                "created_at",
                "canonical_key"
            }
        ]

        available_doctypes = [

            "Purchase Order"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="purchase_orders",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "purchase_orders",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/purchase-orders"
)
def save_purchase_order_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_purchase_order_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_orders",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Purchase Order target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/purchase-order-items"
)
def test_purchase_order_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_purchase_order_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No purchase order items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        available_doctypes = [

            "Purchase Order Item"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="purchase_order_items",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "purchase_order_items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()

@router.post(
    "/target-discovery/save/purchase-order-items"
)
def save_purchase_order_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_purchase_order_item_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Purchase Order Item target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/target-discovery/test/sales-orders"
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

        if not sample_so:

            return {
                "error":
                    "No sales orders found"
            }

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

        available_doctypes = [

            "Sales Order"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="sales_orders",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

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
    "/target-discovery/save/sales-orders"
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
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Sales Order target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }


@router.post(
    "/target-discovery/test/sales-order-items"
)
def test_sales_order_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        sample_item = db.execute(
            text("""
                SELECT *
                FROM unified_sales_order_items
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).mappings().first()

        if not sample_item:

            return {
                "error":
                    "No sales order items found"
            }

        unified_fields = [

            field

            for field in sample_item.keys()

            if field not in {

                "id",
                "tenant_id",
                "user_id",
                "source"
            }
        ]

        available_doctypes = [

            "Sales Order Item"
        ]

        targets = (
            generate_target_doctypes(
                entity_type="sales_order_items",
                unified_fields=unified_fields,
                available_doctypes=available_doctypes
            )
        )

        return {

            "entity_type":
                "sales_order_items",

            "unified_fields":
                unified_fields,

            "recommended_targets":
                targets
        }

    finally:

        db.close()


@router.post(
    "/target-discovery/save/sales-order-items"
)
def save_sales_order_item_target_discovery(

    current_user=Depends(
        get_current_user
    )

):

    discovered = (
        test_sales_order_item_target_discovery(
            current_user
        )
    )

    save_entity_targets(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        target_system=
            "erpnext",

        targets=
            discovered[
                "recommended_targets"
            ]
    )

    return {

        "message":
            "Sales Order Item target discovery saved",

        "targets":
            discovered[
                "recommended_targets"
            ]
    }

@router.post(
    "/mapping/preview/customers"
)
def preview_customer_mapping(

    current_user=Depends(
        get_current_user
    )

):

    return get_complete_mapping(
        tenant_id=
            current_user.tenant_id,
        entity_type=
            "customers",
        source_system=
            "xero",
        target_system=
            "erpnext"
    )

@router.post(
    "/workflow/save/customers"
)
def save_workflow_customer_mapping(

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
            "customers",

        source_system=
            "xero",

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
            config
            ["mapping"]
            .items()
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
            "customers",

        target_system=
            "erpnext",

        mappings=
            target_mappings
    )

    return {

        "message":
            "Workflow saved successfully"
    }

@router.post(
    "/mapping/preview/suppliers"
)
def preview_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):

    return get_complete_mapping(
        tenant_id=
            current_user.tenant_id,
        entity_type=
            "suppliers",
        source_system=
            "xero",
        target_system=
            "erpnext"
    )

@router.post(
    "/workflow/save/suppliers"
)
def save_workflow_supplier_mapping(

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
            "suppliers",

        source_system=
            "xero",

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
            config
            ["mapping"]
            .items()
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
            "suppliers",

        target_system=
            "erpnext",

        mappings=
            target_mappings
    )

    print("PAYLOAD:")
    print(payload.mappings)    

    return {

        "message":
            "Supplier workflow saved successfully"
    }

@router.post(
    "/mapping/preview/items"
)
def preview_item_mapping(

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
            "xero",
        target_system=
            "erpnext"
    )

@router.post(
    "/workflow/save/items"
)
def save_workflow_item_mapping(

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
            "items",

        source_system=
            "xero",

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
            config
            ["mapping"]
            .items()
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
            "erpnext",

        mappings=
            target_mappings
    )

    print("PAYLOAD:")
    print(payload.mappings)    

    return {

        "message":
            "Items workflow saved successfully"
    }

@router.post(
    "/mapping/preview/bills"
)
def preview_bill_mapping(

    current_user=Depends(
        get_current_user
    )

):

    bills = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bills",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    bill_items = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    source_to_unified = {

        **bills.get(
            "source_to_unified",
            {}
        ),

        **bill_items.get(
            "source_to_unified",
            {}
        )
    }

    unified_to_target = {

        **bills.get(
            "unified_to_target",
            {}
        ),

        **bill_items.get(
            "unified_to_target",
            {}
        )
    }

    available_unified_fields = list(

        set(

            bills.get(
                "available_unified_fields",
                []
            )

            +

            bill_items.get(
                "available_unified_fields",
                []
            )
        )
    )

    unified_field_groups = {

        **bills.get(
            "unified_field_groups",
            {}
        ),

        **bill_items.get(
            "unified_field_groups",
            {}
        )
    }

    return {

        "source_to_unified":
            source_to_unified,

        "unified_to_target":
            unified_to_target,

        "available_unified_fields":
            available_unified_fields,

        "unified_field_groups":
            unified_field_groups
    }

@router.post(
    "/workflow/save/bills"
)
def save_workflow_bill_mapping(

    payload: WorkflowSaveRequest,

    current_user=Depends(
        get_current_user
    )

):

    print("=" * 50)
    print("WORKFLOW PAYLOAD")
    print(payload.dict())
    print("=" * 50)

    bill_fields = {

        "external_id",
        "bill_number",
        "supplier_name",
        "bill_date",
        "due_date",
        "subtotal",
        "tax_amount",
        "total_amount",
        "status"
    }

    bill_item_fields = {

        "item_external_id",
        "item_code",
        "item_name",
        "quantity",
        "unit_price",
        "line_total"
    }

    #
    # SOURCE → UNIFIED
    #

    bill_source_mapping = {}
    bill_item_source_mapping = {}

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

        if unified_field in bill_fields:

            bill_source_mapping[
                source_field
            ] = unified_field

        elif unified_field in bill_item_fields:

            bill_item_source_mapping[
                source_field
            ] = unified_field

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bills",

        source_system=
            "xero",

        mapping=
            bill_source_mapping
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        source_system=
            "xero",

        mapping=
            bill_item_source_mapping
    )

    #
    # UNIFIED → ERPNEXT
    #

    bill_target_mappings = {}
    bill_item_target_mappings = {}

    for doctype, config in (
        payload
        .mappings
        ["unified_to_target"]
        .items()
    ):

        if doctype == "Purchase Invoice":

            bill_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                bill_target_mappings[
                    doctype
                ][
                    "mapping"
                ][
                    unified_field
                ] = target_field

        elif doctype == "Purchase Invoice Item":

            bill_item_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                bill_item_target_mappings[
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
            "bills",

        target_system=
            "erpnext",

        mappings=
            bill_target_mappings
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "bill_items",

        target_system=
            "erpnext",

        mappings=
            bill_item_target_mappings
    )

    return {

        "message":
            "Bills workflow saved successfully"
    }

@router.post(
    "/mapping/preview/invoices"
)
def preview_invoice_mapping(

    current_user=Depends(
        get_current_user
    )

):

    invoices = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoices",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    invoice_items = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    source_to_unified = {

        **invoices.get(
            "source_to_unified",
            {}
        ),

        **invoice_items.get(
            "source_to_unified",
            {}
        )
    }

    unified_to_target = {

        **invoices.get(
            "unified_to_target",
            {}
        ),

        **invoice_items.get(
            "unified_to_target",
            {}
        )
    }

    available_unified_fields = list(

        set(

            invoices.get(
                "available_unified_fields",
                []
            )

            +

            invoice_items.get(
                "available_unified_fields",
                []
            )
        )
    )

    unified_field_groups = {

        **invoices.get(
            "unified_field_groups",
            {}
        ),

        **invoice_items.get(
            "unified_field_groups",
            {}
        )
    }

    return {

        "source_to_unified":
            source_to_unified,

        "unified_to_target":
            unified_to_target,

        "available_unified_fields":
            available_unified_fields,

        "unified_field_groups":
            unified_field_groups
    }


@router.post(
    "/workflow/save/invoices"
)
def save_workflow_invoice_mapping(

    payload: WorkflowSaveRequest,

    current_user=Depends(
        get_current_user
    )

):

    print("=" * 50)
    print("WORKFLOW PAYLOAD")
    print(payload.dict())
    print("=" * 50)

    invoice_fields = {

        "external_id",
        "invoice_number",
        "customer_name",
        "invoice_date",
        "due_date",
        "subtotal",
        "tax_amount",
        "total_amount",
        "currency",
        "status"
    }

    invoice_item_fields = {

        "item_external_id",
        "item_code",
        "item_name",
        "quantity",
        "unit_price",
        "line_total"
    }

    #
    # SOURCE → UNIFIED
    #

    invoice_source_mapping = {}
    invoice_item_source_mapping = {}

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

        if unified_field in invoice_fields:

            invoice_source_mapping[
                source_field
            ] = unified_field

        elif unified_field in invoice_item_fields:

            invoice_item_source_mapping[
                source_field
            ] = unified_field

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoices",

        source_system=
            "xero",

        mapping=
            invoice_source_mapping
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        source_system=
            "xero",

        mapping=
            invoice_item_source_mapping
    )

    #
    # UNIFIED → ERPNEXT
    #

    invoice_target_mappings = {}
    invoice_item_target_mappings = {}

    for doctype, config in (
        payload
        .mappings
        ["unified_to_target"]
        .items()
    ):

        if doctype == "Sales Invoice":

            invoice_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                invoice_target_mappings[
                    doctype
                ][
                    "mapping"
                ][
                    unified_field
                ] = target_field

        elif doctype == "Sales Invoice Item":

            invoice_item_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                invoice_item_target_mappings[
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
            "invoices",

        target_system=
            "erpnext",

        mappings=
            invoice_target_mappings
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "invoice_items",

        target_system=
            "erpnext",

        mappings=
            invoice_item_target_mappings
    )

    return {

        "message":
            "Invoices workflow saved successfully"
    }

@router.post(
    "/mapping/preview/purchase-orders"
)
def preview_purchase_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    purchase_orders = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_orders",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    purchase_order_items = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    source_to_unified = {

        **purchase_orders.get(
            "source_to_unified",
            {}
        ),

        **purchase_order_items.get(
            "source_to_unified",
            {}
        )
    }

    unified_to_target = {

        **purchase_orders.get(
            "unified_to_target",
            {}
        ),

        **purchase_order_items.get(
            "unified_to_target",
            {}
        )
    }

    available_unified_fields = list(

        set(

            purchase_orders.get(
                "available_unified_fields",
                []
            )

            +

            purchase_order_items.get(
                "available_unified_fields",
                []
            )
        )
    )

    unified_field_groups = {

        **purchase_orders.get(
            "unified_field_groups",
            {}
        ),

        **purchase_order_items.get(
            "unified_field_groups",
            {}
        )
    }

    return {

        "source_to_unified":
            source_to_unified,

        "unified_to_target":
            unified_to_target,

        "available_unified_fields":
            available_unified_fields,

        "unified_field_groups":
            unified_field_groups
    }

@router.post(
    "/workflow/save/purchase-orders"
)
def save_workflow_purchase_order_mapping(

    payload: WorkflowSaveRequest,

    current_user=Depends(
        get_current_user
    )

):

    print("=" * 50)
    print("WORKFLOW PAYLOAD")
    print(payload.dict())
    print("=" * 50)

    purchase_order_fields = {

        "external_id",
        "po_number",
        "supplier_name",
        "order_date",
        "delivery_date",
        "total_amount",
        "status"
    }

    purchase_order_item_fields = {

        "item_external_id",
        "item_code",
        "item_name",
        "quantity",
        "unit_price",
        "line_total"
    }

    #
    # SOURCE → UNIFIED
    #

    po_source_mapping = {}
    po_item_source_mapping = {}

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

        if unified_field in purchase_order_fields:

            po_source_mapping[
                source_field
            ] = unified_field

        elif unified_field in purchase_order_item_fields:

            po_item_source_mapping[
                source_field
            ] = unified_field

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_orders",

        source_system=
            "xero",

        mapping=
            po_source_mapping
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        source_system=
            "xero",

        mapping=
            po_item_source_mapping
    )

    #
    # UNIFIED → ERPNEXT
    #

    po_target_mappings = {}
    po_item_target_mappings = {}

    for doctype, config in (
        payload
        .mappings
        ["unified_to_target"]
        .items()
    ):

        if doctype == "Purchase Order":

            po_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                po_target_mappings[
                    doctype
                ][
                    "mapping"
                ][
                    unified_field
                ] = target_field

        elif doctype == "Purchase Order Item":

            po_item_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                po_item_target_mappings[
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
            "purchase_orders",

        target_system=
            "erpnext",

        mappings=
            po_target_mappings
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "purchase_order_items",

        target_system=
            "erpnext",

        mappings=
            po_item_target_mappings
    )

    return {

        "message":
            "Purchase Orders workflow saved successfully"
    }

@router.post(
    "/mapping/preview/sales-orders"
)
def preview_sales_order_mapping(

    current_user=Depends(
        get_current_user
    )

):

    sales_orders = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_orders",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    sales_order_items = get_complete_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        source_system=
            "xero",

        target_system=
            "erpnext"
    )

    source_to_unified = {

        **sales_orders.get(
            "source_to_unified",
            {}
        ),

        **sales_order_items.get(
            "source_to_unified",
            {}
        )
    }

    unified_to_target = {

        **sales_orders.get(
            "unified_to_target",
            {}
        ),

        **sales_order_items.get(
            "unified_to_target",
            {}
        )
    }

    available_unified_fields = list(

        set(

            sales_orders.get(
                "available_unified_fields",
                []
            )

            +

            sales_order_items.get(
                "available_unified_fields",
                []
            )
        )
    )

    unified_field_groups = {

        **sales_orders.get(
            "unified_field_groups",
            {}
        ),

        **sales_order_items.get(
            "unified_field_groups",
            {}
        )
    }

    return {

        "source_to_unified":
            source_to_unified,

        "unified_to_target":
            unified_to_target,

        "available_unified_fields":
            available_unified_fields,

        "unified_field_groups":
            unified_field_groups
    }

@router.post(
    "/workflow/save/sales-orders"
)
def save_workflow_sales_order_mapping(

    payload: WorkflowSaveRequest,

    current_user=Depends(
        get_current_user
    )

):

    print("=" * 50)
    print("WORKFLOW PAYLOAD")
    print(payload.dict())
    print("=" * 50)

    sales_order_fields = {

        "external_id",
        "so_number",
        "customer_name",
        "order_date",
        "delivery_date",
        "total_amount",
        "status"
    }

    sales_order_item_fields = {

        "item_external_id",
        "item_code",
        "item_name",
        "quantity",
        "unit_price",
        "line_total"
    }

    #
    # SOURCE → UNIFIED
    #

    so_source_mapping = {}
    so_item_source_mapping = {}

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

        if unified_field in sales_order_fields:

            so_source_mapping[
                source_field
            ] = unified_field

        elif unified_field in sales_order_item_fields:

            so_item_source_mapping[
                source_field
            ] = unified_field

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_orders",

        source_system=
            "xero",

        mapping=
            so_source_mapping
    )

    save_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        source_system=
            "xero",

        mapping=
            so_item_source_mapping
    )

    #
    # UNIFIED → ERPNEXT
    #

    so_target_mappings = {}
    so_item_target_mappings = {}

    for doctype, config in (
        payload
        .mappings
        ["unified_to_target"]
        .items()
    ):

        if doctype == "Sales Order":

            so_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                so_target_mappings[
                    doctype
                ][
                    "mapping"
                ][
                    unified_field
                ] = target_field

        elif doctype == "Sales Order Item":

            so_item_target_mappings[
                doctype
            ] = {
                "mapping": {}
            }

            for unified_field, target_field in (
                config
                ["mapping"]
                .items()
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

                so_item_target_mappings[
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
            "sales_orders",

        target_system=
            "erpnext",

        mappings=
            so_target_mappings
    )

    save_target_mapping(

        tenant_id=
            current_user.tenant_id,

        entity_type=
            "sales_order_items",

        target_system=
            "erpnext",

        mappings=
            so_item_target_mappings
    )

    return {

        "message":
            "Sales Orders workflow saved successfully"
    }