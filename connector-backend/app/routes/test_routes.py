from fastapi import APIRouter, Depends
import requests
from sqlalchemy import text
from app.database import engine
from app.database import SessionLocal
import json

from app.dependencies.auth import (
    get_current_user
)
from app.services.xero_fetch_service import (
    fetch_complete_xero_suppliers,
    fetch_complete_xero_items
)

from app.services.mapping_service import (
    get_complete_mapping,
    get_target_mappings,
    build_payload_from_mapping,
    generate_mapping,
    save_mapping,
    get_table_columns
)

from app.services.testing import (
    generate_testing
)

from app.services.erpnext_fetch_service import (
    fetch_complete_erpnext_customers,
    fetch_complete_erpnext_suppliers,
    fetch_erpnext_complete_items
)


from app.services.erpnext_metadata_service import (
    get_erpnext_doctype_fields
)

from app.services.xero_auth_service import (
    refresh_xero_token
)

router = APIRouter(
    tags=["Testing"]
)

@router.get(
    "/mapping/test/suppliers"
)
def test_suppliers(

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

    return {
        "total_suppliers":
            len(suppliers),

        "first_supplier":
            suppliers[0]
            if suppliers
            else None
    }

@router.get(
    "/mapping/test/suppliers/test"
)
def test_suppliers(

    number: str,
    content: str,

    current_user=Depends(
        get_current_user
    )

):
    gen = generate_testing(number,content)

    return gen

@router.get(
    "/mapping/test/items"
)
def test_items(

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

    return {

        "total_items":
            len(items),

        "first_item":
            items[0]
            if items else None
    }

@router.get(
    "/mapping/test/bills"
)
def test_bills(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {

            "Authorization":
                f"Bearer {integration.access_token}",

            "Xero-tenant-id":
                integration.tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Invoices",
            headers=headers
        )

        invoices = response.json().get(
            "Invoices",
            []
        )

        bills = []

        for invoice in invoices:

            if invoice.get(
                "Type"
            ) == "ACCPAY":
                
                print(
            invoice.get("InvoiceNumber"),
            invoice.get("Status")
        )        

                bills.append(
                    invoice
                )

        return {
            "total_bills":
                len(bills),

            "first_bill":
                bills[0]
                if bills
                else None
        }

    finally:

        db.close()

@router.get(
    "/mapping/test/sales-orders"
)
def test_sales_orders(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {

            "Authorization":
                f"Bearer {integration.access_token}",

            "Xero-tenant-id":
                integration.tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Quotes",
            headers=headers
        )

        data = response.json()

        print(data)

        quotes = response.json().get(
            "Quotes",
            []
        )
        for quote in quotes:

            print(
                quote.get("QuoteNumber"),
                quote.get("Status")
            )

        return {
            "total_quotes":
                len(quotes),

            "first_quote":
                quotes[0]
                if quotes
                else None
        }

    finally:

        db.close()

@router.get(
    "/mapping/test/purchase-orders"
)
def test_purchase_orders(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {

            "Authorization":
                f"Bearer {integration.access_token}",

            "Xero-tenant-id":
                integration.tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/PurchaseOrders",
            headers=headers
        )

        purchase_orders = (
            response.json().get(
                "PurchaseOrders",
                []
            )
        )

        for porder in purchase_orders:

            print(
                porder.get("Status")
            )

        return {
            "total_purchase_orders":
                len(
                    purchase_orders
                ),

            "first_purchase_order":
                purchase_orders[0]
                if purchase_orders
                else None
        }

    finally:

        db.close()

@router.get(
    "/mapping/test/accounts"
)
def test_accounts(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {

            "Authorization":
                f"Bearer {integration.access_token}",

            "Xero-tenant-id":
                integration.tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Accounts",
            headers=headers
        )

        accounts = (
            response.json().get(
                "Accounts",
                []
            )
        )

        return {

            "total_accounts":
                len(accounts),

            "first_account":
                accounts[0]
                if accounts
                else None
        }

    finally:

        db.close()

@router.get(
    "/erpnext/test/accounts"
)
def test_erpnext_accounts(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
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
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        response = requests.get(
            f"{erp.erp_url}/api/resource/Account?limit_page_length=1",
            headers=headers
        )

        return response.json()

    finally:

        db.close()

@router.get(
    "/erpnext/test/account-details"
)
def test_account_details(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
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
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        account_name = requests.get(
            f"{erp.erp_url}/api/resource/Account?limit_page_length=1",
            headers=headers
        ).json()["data"][0]["name"]

        response = requests.get(
            f"{erp.erp_url}/api/resource/Account/{account_name}",
            headers=headers
        )

        return response.json()

    finally:

        db.close()

@router.get(
    "/erpnext/test/company"
)
def test_company(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        response = requests.get(
            f"{erp.erp_url}/api/resource/Company",
            headers=headers
        )

        return response.json()

    finally:

        db.close()

@router.get(
    "/erpnext/test/root-accounts"
)
def test_root_accounts(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        tenant_id = db.execute(
            text("""
                SELECT tenant_id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": current_user.id
            }
        ).scalar()

        erp = db.execute(
            text("""
                SELECT *
                FROM erpnext_integrations
                WHERE tenant_id = :tenant_id
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id
            }
        ).fetchone()

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        response = requests.get(
            f"{erp.erp_url}/api/resource/Account?fields=[\"name\",\"account_name\",\"root_type\",\"is_group\"]&limit_page_length=200",
            headers=headers
        )

        return response.json()

    finally:

        db.close()

@router.get(
    "/erpnext/test/account-fields"
)
def test_account_fields(

    current_user=Depends(
        get_current_user
    )

):

    fields = get_erpnext_doctype_fields(
        current_user.tenant_id,
        "Account"
    )

    return {
        "total_fields":
            len(fields),

        "fields":
            fields
    }

@router.get("/test-complete-mapping")
def test_complete_mapping(

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

@router.get(
    "/test-target-mappings"
)
def test_target_mappings():

    return get_target_mappings(
        tenant_id=1,
        entity_type="customers",
        target_system="erpnext"
    )

@router.get(
    "/test-build-payload"
)
def test_build_payload():

    db = SessionLocal()

    try:

        customer = db.execute(
            text("""
                SELECT *
                FROM unified_customers
                WHERE tenant_id = 1
                LIMIT 1
            """)
        ).fetchone()

        mappings = get_target_mappings(
            tenant_id=1,
            entity_type="customers",
            target_system="erpnext"
        )

        return {
            "customer_payload":
                build_payload_from_mapping(
                    customer,
                    mappings["Customer"]
                ),

            "contact_payload":
                build_payload_from_mapping(
                    customer,
                    mappings["Contact"]
                ),

            "address_payload":
                build_payload_from_mapping(
                    customer,
                    mappings["Address"]
                )
        }

    finally:

        db.close()


@router.get(
    "/xero/items/sample"
)
def get_xero_item_sample(

    current_user=Depends(
        get_current_user
    )

):

    db = SessionLocal()

    try:

        integration = db.execute(
            text("""
                SELECT *
                FROM integrations
                WHERE
                    tenant_id_fk = :tenant_id
                    AND provider = 'xero'
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "tenant_id":
                    current_user.tenant_id
            }
        ).fetchone()

        if not integration:

            return {
                "error":
                    "No Xero integration found"
            }

        access_token = (
            integration.access_token
        )

        xero_tenant_id = (
            integration.tenant_id
        )

        url = (
            "https://api.xero.com/"
            "api.xro/2.0/Items"
        )

        headers = {

            "Authorization":
                f"Bearer {access_token}",

            "Xero-tenant-id":
                xero_tenant_id,

            "Accept":
                "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )

        data = response.json()

        if response.status_code == 401:

            refreshed = (
                refresh_xero_token(
                    integration.id
                )
            )

            access_token = (
                refreshed[
                    "access_token"
                ]
            )

            headers[
                "Authorization"
            ] = (
                f"Bearer {access_token}"
            )

            response = requests.get(
                url,
                headers=headers
            )

            data = response.json()

        items = data.get(
            "Items",
            []
        )

        if not items:

            return {
                "message":
                    "No items found"
            }

        return {

            "sample_item":
                items[0],

            "source_fields":
                list(
                    items[0].keys()
                ),

            "total_items":
                len(items)
        }

    finally:

        db.close()

@router.post(
    "/source-discovery/test/customers/erpnext"
)
def test_erpnext_customer_source_discovery(

    current_user=Depends(
        get_current_user
    )

):

    customers = (
        fetch_complete_erpnext_customers(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not customers:

        return {
            "error":
                "No ERPNext customers found"
        }

    sample_customer = customers[0]

    source_fields = list(
        sample_customer.keys()
    )

    destination_fields = [

        "external_id",
        "customer_name",
        "email",
        "phone",
        "address",
        "tax_number",
        "website",
        "status",
        "contact_name",
        "postal_code",
        "city",
        "state",
        "country"
    ]

    mapping = generate_mapping(

        "customers",

        source_fields,

        destination_fields,

        sample_customer
    )

    return {

        "sample_customer":
            sample_customer,

        "source_fields":
            source_fields,

        "destination_fields":
            destination_fields,

        "mapping":
            mapping
    }

@router.post(
    "/source-discovery/save/customers/erpnext"
)
def save_erpnext_customer_source_discovery(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        test_erpnext_customer_source_discovery(
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
            "customers",

        source_system=
            "erpnext",

        mapping=
            mapping
    )

    return {

        "message":
            "ERPNext Customer mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/erpnext-suppliers"
)
def generate_erpnext_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):

    suppliers = (
        fetch_complete_erpnext_suppliers(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not suppliers:

        return {
            "error":
                "No ERPNext suppliers found"
        }

    sample_supplier = suppliers[0]

    source_fields = [

        "supplier_name",
        "contact_name",
        "email",
        "phone",
        "address",
        "postal_code"
    ]

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
            "tenant_id",
            "user_id",
            "source",
            "created_at"
        }
    ]

    mapping = generate_mapping(

        "erpnext_suppliers",

        source_fields,

        destination_fields,

        sample_supplier
    )

    return {

        "sample_supplier":
            sample_supplier,

        "source_fields":
            source_fields,

        "destination_fields":
            destination_fields,

        "mapping":
            mapping
    }

@router.post(
    "/mapping/save/erpnext-suppliers"
)
def save_erpnext_supplier_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_erpnext_supplier_mapping(
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
            "erpnext_suppliers",

        source_system=
            "erpnext",

        mapping=
            mapping
    )

    return {

        "message":
            "ERPNext Supplier mappings saved",

        "mapping":
            mapping
    }

@router.post(
    "/mapping/generate/erpnext-items"
)
def generate_erpnext_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    items = (
        fetch_erpnext_complete_items(
            current_user.id,
            current_user.tenant_id
        )
    )

    if not items:

        return {
            "error":
                "No ERPNext items found"
        }

    sample_item = items[0]

    source_fields = [

        "name",
        "item_code",
        "item_name",
        "description",
        "standard_rate",
        "valuation_rate",
        "is_stock_item",
        "disabled",
        "gst_hsn_code"
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
            "tenant_id",
            "user_id",
            "source",
            "created_at"
        }
    ]

    mapping = generate_mapping(

        "erpnext_items",

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
    "/mapping/save/erpnext-items"
)
def save_erpnext_item_mapping(

    current_user=Depends(
        get_current_user
    )

):

    generated = (
        generate_erpnext_item_mapping(
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
            "erpnext_items",

        source_system=
            "erpnext",

        mapping=
            mapping
    )

    return {

        "message":
            "ERPNext Item mappings saved",

        "mapping":
            mapping
    }

