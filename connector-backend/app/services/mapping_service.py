from groq import Groq
import os
import re
import json
from sqlalchemy import text
from datetime import datetime
from app.database import SessionLocal
from app.services.erpnext_metadata_service import (
    get_erpnext_doctype_fields
)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_mapping(
    entity_type,
    source_fields,
    destination_fields,
    sample_record
):
    
    entity_rules = ""

    if entity_type == "customers":

        entity_rules = """
    Customer Rules:

    - Name maps to customer_name.
    - ContactPersons maps to contact_name.
    - FirstName + LastName maps to contact_name.
    - EmailAddress maps to email.
    - Phones maps to phone.
    - Addresses maps to address.
    - City maps to city.
    - State maps to state.
    - Country maps to country.
    - PostalCode maps to postal_code.
    - TaxNumber maps to tax_number.
    - Website maps to website.
    - ContactStatus maps to status.
    """

    elif entity_type == "suppliers":

        entity_rules = """
    Supplier Rules:

    - Name maps to supplier_name.
    - ContactPersons maps to contact_name.
    - FirstName + LastName maps to contact_name.
    - EmailAddress maps to email.
    - Phones maps to phone.
    - Addresses maps to address.
    - PostalCode maps to postal_code.
    - TaxNumber maps to tax_number.
    - Website maps to website.
    - ContactStatus maps to status.
    """
        
    elif entity_type == "items":

        entity_rules = """
    Item Rules:

    - ItemID maps to external_id.
    - Code maps to item_code.
    - Name maps to item_name.
    - Description maps to description.
    - SalesDetails.UnitPrice maps to selling_price.
    - PurchaseDetails.UnitPrice maps to purchase_price.
    - Status maps to status.
    """
        
    elif entity_type == "invoices":

        entity_rules = """
    Invoice Rules:

    - InvoiceID maps to external_id.
    - InvoiceNumber maps to invoice_number.
    - Contact.Name maps to customer_name.
    - Date maps to invoice_date.
    - DueDate maps to due_date.
    - SubTotal maps to subtotal.
    - TotalTax maps to tax_amount.
    - Total maps to total_amount.
    - CurrencyCode maps to currency.
    - Status maps to status.
    """
        
    elif entity_type == "invoice_items":

        entity_rules = """
    Invoice Item Rules:

    - Item.ItemID maps to item_external_id.
    - ItemCode maps to item_code.
    - Description maps to item_name.
    - Quantity maps to quantity.
    - UnitAmount maps to unit_price.
    - LineAmount maps to line_total.

    CRITICAL:

    - LEFT side MUST be a Xero source field.
    - RIGHT side MUST be a Unified field.
    - NEVER reverse the mapping.
    """
        
    elif entity_type == "bills":

        entity_rules = """
    Bill Rules:

    - InvoiceID maps to external_id.
    - InvoiceNumber maps to bill_number.
    - Contact.Name maps to supplier_name.
    - Date maps to bill_date.
    - DueDate maps to due_date.
    - SubTotal maps to subtotal.
    - TotalTax maps to tax_amount.
    - Total maps to total_amount.
    - Status maps to status.
    """    
        
    elif entity_type == "bill_items":

        entity_rules = """
    Bill Item Rules:

    - Item.ItemID maps to item_external_id.
    - ItemCode maps to item_code.
    - Description maps to item_name.
    - Quantity maps to quantity.
    - UnitAmount maps to unit_price.
    - LineAmount maps to line_total.

    CRITICAL:

    - LEFT side MUST be a Xero source field.
    - RIGHT side MUST be a Unified field.
    - NEVER reverse the mapping.
    """
        
    elif entity_type == "sales_orders":

        entity_rules = """
    Sales Order Rules:

    - QuoteID maps to external_id.
    - QuoteNumber maps to so_number.
    - Contact.Name maps to customer_name.
    - Date maps to order_date.
    - ExpiryDate maps to delivery_date.
    - Total maps to total_amount.
    - Status maps to status.
    """
        
    elif entity_type == "sales_order_items":

        entity_rules = """
    Sales Order Item Rules:

    - LineItemID maps to item_external_id.
    - ItemCode maps to item_code.
    - Description maps to item_name.
    - Quantity maps to quantity.
    - UnitAmount maps to unit_price.
    - LineAmount maps to line_total.

    CRITICAL:

    - LEFT side MUST be a Xero source field.
    - RIGHT side MUST be a Unified field.
    - NEVER reverse the mapping.
    """
        
    elif entity_type == "erpnext_sales_orders":

        entity_rules = """
    ERPNext Sales Order Rules:

    - name maps to so_number
    - customer maps to customer_name
    - customer_name maps to customer_name
    - transaction_date maps to order_date
    - delivery_date maps to delivery_date
    - grand_total maps to total_amount
    - rounded_total maps to total_amount
    - status maps to status

    CRITICAL:

    - LEFT side MUST be ERPNext fields
    - RIGHT side MUST be Unified fields

    Examples:

    name -> so_number
    customer -> customer_name
    transaction_date -> order_date
    delivery_date -> delivery_date
    grand_total -> total_amount
    status -> status
    """
        
    elif entity_type == "erpnext_sales_order_items":

        entity_rules = """
    ERPNext Sales Order Item Rules:

    - parent maps to so_external_id
    - item_code maps to item_code
    - item_name maps to item_name
    - qty maps to quantity
    - rate maps to unit_price
    - amount maps to line_total

    CRITICAL:

    LEFT side MUST be ERPNext fields

    RIGHT side MUST be Unified fields

    Examples:

    parent -> so_external_id
    item_code -> item_code
    item_name -> item_name
    qty -> quantity
    rate -> unit_price
    amount -> line_total
    """
        
    elif entity_type == "purchase_orders":

        entity_rules = """
    Purchase Order Rules:

    - PurchaseOrderID maps to external_id.
    - PurchaseOrderNumber maps to po_number.
    - Contact.Name maps to supplier_name.
    - Date maps to order_date.
    - DeliveryDate maps to delivery_date.
    - Total maps to total_amount.
    - Status maps to status.
    """
        
    elif entity_type == "purchase_order_items":

        entity_rules = """
    Purchase Order Item Rules:

    - LineItemID maps to item_external_id.
    - ItemCode maps to item_code.
    - Description maps to item_name.
    - Quantity maps to quantity.
    - UnitAmount maps to unit_price.
    - LineAmount maps to line_total.

    CRITICAL:

    - LEFT side MUST be a Xero source field.
    - RIGHT side MUST be a Unified field.
    - NEVER reverse the mapping.
    """
        
    elif entity_type == "accounts":

        entity_rules = """
    Account Rules:

    - AccountID maps to account_id.
    - Code maps to account_code.
    - Name maps to account_name.
    - Type maps to account_type.
    - Class maps to account_class.
    - Description maps to description.
    - Status maps to status.
    """
        
    elif entity_type == "erpnext_suppliers":

        entity_rules = """
    ERPNext Supplier Rules:

    - supplier_name maps to supplier_name.
    - contact_name maps to contact_name.
    - email maps to email.
    - phone maps to phone.
    - address maps to address.
    - postal_code maps to postal_code.

    CRITICAL:

    - LEFT side MUST be ERPNext fields.
    - RIGHT side MUST be Unified fields.
    - NEVER reverse the mapping.
    """
        
    elif entity_type == "erpnext_items":

        entity_rules = """
    ERPNext Item Rules:

    - name maps to external_id.
    - item_code maps to item_code.
    - item_name maps to item_name.
    - description maps to description.

    - standard_rate maps to sales_price.
    - valuation_rate maps to purchase_price.

    - is_stock_item maps to is_inventory.
    - is_sales_item maps to is_sold.
    - is_purchase_item maps to is_purchased.

    - gst_hsn_code maps to hsn_code.

    CRITICAL:

    - LEFT side MUST be ERPNext fields.
    - RIGHT side MUST be Unified fields.
    - NEVER reverse the mapping.
    """

    prompt = f"""
You are an ERP migration expert.

Map source fields to destination fields based on BUSINESS MEANING.

{entity_rules}

IMPORTANT:

Do not map anything to:

id
user_id
tenant_id
created_at
updated_at
source

Return ONLY valid JSON.

Example:

{{
  "ContactID": "external_id",
  "Name": "customer_name",
  "EmailAddress": "email"
}}

Sample Record:
{json.dumps(sample_record, indent=2)}

Source Fields:
{source_fields}

Destination Fields:
{destination_fields}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()

    print("GROQ RESPONSE:")
    print(content)

    import re

    matches = re.findall(
        r'\{[\s\S]*?\}',
        content
    )

    if not matches:

        raise Exception(
            f"No JSON found in AI response:\n{content}"
        )

    json_text = matches[-1]

    return json.loads(
        json_text
    )

def get_table_columns(table_name):

    db = SessionLocal()

    try:

        columns = db.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """),
            {
                "table_name": table_name
            }
        ).fetchall()

        return [
            row[0]
            for row in columns
        ]

    finally:

        db.close()

def save_mapping(
    tenant_id,
    entity_type,
    source_system,
    mapping
):

    db = SessionLocal()

    try:

        db.execute(
            text("""
                DELETE FROM field_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND source_system = :source_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "source_system": source_system
            }
        )

        for source_field, destination_field in mapping.items():

            db.execute(
                text("""
                    INSERT INTO field_mappings
                    (
                        tenant_id,
                        entity_type,
                        source_system,
                        source_field,
                        destination_field,
                        confidence,
                        created_at
                    )
                    VALUES
                    (
                        :tenant_id,
                        :entity_type,
                        :source_system,
                        :source_field,
                        :destination_field,
                        :confidence,
                        :created_at
                    )
                """),
                {
                    "tenant_id": tenant_id,

                    "entity_type": entity_type,

                    "source_system": source_system,

                    "source_field": source_field,

                    "destination_field":
                        destination_field,

                    "confidence": 1.0,

                    "created_at":
                        datetime.utcnow()
                }
            )

        db.commit()

        return {
            "message":
                "Mapping saved successfully"
        }

    finally:

        db.close()


def get_mapping(
    tenant_id,
    entity_type,
    source_system
):

    db = SessionLocal()

    try:

        mappings = db.execute(
            text("""
                SELECT
                    source_field,
                    destination_field,
                    confidence,
                    created_at
                FROM field_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND source_system = :source_system
                ORDER BY id
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "source_system": source_system
            }
        ).fetchall()

        return [

            {
                "source_field":
                    row.source_field,

                "destination_field":
                    row.destination_field,

                "confidence":
                    float(
                        row.confidence
                    ),

                "created_at":
                    row.created_at
            }

            for row in mappings

        ]

    finally:

        db.close()


def get_mapping_dict(
    tenant_id,
    entity_type,
    source_system
):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT
                    source_field,
                    destination_field
                FROM field_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND source_system = :source_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "source_system": source_system
            }
        ).fetchall()

        print("ROWS:", rows)

        print("=" * 80)
        print("QUERY TENANT:", tenant_id)
        print("QUERY ENTITY:", entity_type)
        print("QUERY SOURCE:", source_system)
        print("=" * 80)

        return {

            row.source_field:
                row.destination_field

            for row in rows

        }

    finally:

        db.close()


def generate_target_mapping(
    entity_type,
    target_doctype,
    unified_fields,
    target_fields,
    sample_record
):

    doctype_rules = ""

    if target_doctype == "Customer":

        doctype_rules = """
Customer Rules:

- customer_name maps to customer_name.
- website maps to website when available.
- tax_number maps to tax_id or gstin when appropriate.
- status maps to disabled only if meaning matches.
- Do NOT map email.
- Do NOT map phone.
- Do NOT map address.
- Do NOT map postal_code.
- Do NOT map city.
- Do NOT map state.
- Do NOT map country.
- Do NOT map external_id.
- Only map fields belonging to the Customer document itself.
"""

    elif target_doctype == "Contact":

        doctype_rules = """
Contact Rules:

- email maps to email_id.
- phone maps to mobile_no.
- contact_name maps to first_name.
- customer_name maps to company_name.
- Do NOT map address.
- Do NOT map postal_code.
- Do NOT map city.
- Do NOT map state.
- Do NOT map country.
- Do NOT map external_id.
"""

    elif target_doctype == "Address":

        doctype_rules = """
Address Rules:

- address maps to address_line1.
- postal_code maps to pincode.
- city maps to city.
- state maps to state.
- country maps to country.
- Do NOT map customer_name.
- Do NOT map email.
- Do NOT map phone.
- Do NOT map external_id.
- Do NOT map address to address references.
"""

    elif target_doctype == "Supplier":

        doctype_rules = """
Supplier Rules:

- supplier_name maps to supplier_name.
- website maps to website when available.
- tax_number maps to tax_id or gstin when appropriate.
- email maps to email_id when available.
- phone maps to mobile_no when available.
- country maps to country.

- Do NOT map contact_name to supplier_primary_contact.
- Do NOT map address.
- Do NOT map postal_code.
- Do NOT map city.
- Do NOT map state.
- Do NOT map external_id.

- supplier_primary_contact is a system-generated ERPNext link field.
- supplier_primary_address is a system-generated ERPNext link field.
- Never map values to supplier_primary_contact.
- Never map values to supplier_primary_address.
"""

    elif target_doctype == "Item":

        doctype_rules = """
Item Rules:

- item_code maps to item_code.
- item_name maps to item_name.
- description maps to description.
- sales_price maps to standard_rate.
- purchase_price maps to valuation_rate.
- is_inventory maps to is_stock_item.
- external_id should not map to item_code.
"""

    elif target_doctype == "Price List":

        doctype_rules = """
Price List Rules:

- sales_price maps to price_list_rate when available.
- purchase_price maps to price_list_rate when available.
- item_code may map to item_code.
- item_name may map to item_name.
- Do not map description.
- Do not map external_id.
"""

    elif target_doctype == "Purchase Invoice":

        doctype_rules = """
Purchase Invoice Rules:

- bill_number maps to bill_no when available.
- supplier_name maps to supplier.
- bill_date maps to posting_date.
- due_date maps to due_date.
- subtotal maps to net_total when available.
- tax_amount maps to total_taxes_and_charges when available.
- total_amount maps to grand_total when available.
- status maps to status when available.

- external_id should not map to supplier.
- external_id should not map to bill_no.

Only map fields belonging to Purchase Invoice.
"""

    elif target_doctype == "Purchase Invoice Item":

        doctype_rules = """
Purchase Invoice Item Rules:

- item_code maps to item_code.
- item_name maps to item_name.
- quantity maps to qty.
- unit_price maps to rate.
- line_total maps to amount.

- item_external_id should only map if an exact ERPNext field exists.

Only map fields belonging to Purchase Invoice Item.
"""

    elif target_doctype == "Sales Invoices":

        doctype_rules = """
Sales Invoice Rules:

- invoice_number maps to naming_series
- customer_name maps to customer
- invoice_date maps to posting_date
- due_date maps to due_date
- subtotal maps to net_total
- tax_amount maps to total_taxes_and_charges
- total_amount maps to grand_total
- currency maps to currency
- status maps to status

CRITICAL:

- never map to ERPNext internal ID fields
- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    elif target_doctype == "Sales Invoice Items":

        doctype_rules = """
Sales Invoice Item Rules:

- item_code maps to item_code.
- item_name maps to item_name.
- quantity maps to qty.
- unit_price maps to rate.
- line_total maps to amount.

CRITICAL:

- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    elif target_doctype == "Purchase Order":

        doctype_rules = """
Purchase Order Rules:

- po_number maps to naming_series when available.
- supplier_name maps to supplier.
- order_date maps to transaction_date.
- delivery_date maps to schedule_date.
- total_amount maps to grand_total when available.
- status maps to status when available.

- external_id should not map to supplier.
- external_id should not map to naming_series.
- external_id should not map to name.

- supplier_name should NEVER map to supplier_name.
- supplier_name must map to supplier.

- order_date should NEVER map to creation.
- order_date should map to transaction_date.

- delivery_date should map to schedule_date.

Only map fields belonging to Purchase Order.

CRITICAL:

- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    elif target_doctype == "Purchase Order Item":

        doctype_rules = """
Purchase Order Item Rules:

- item_code maps to item_code.
- item_name maps to item_name.
- quantity maps to qty.
- unit_price maps to rate.
- line_total maps to amount.

- item_external_id should only map if an exact ERPNext field exists.
- po_external_id should not map unless an exact ERPNext field exists.

Only map fields belonging to Purchase Order Item.

CRITICAL:

- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    elif target_doctype == "Sales Order":

        doctype_rules = """
Sales Order Rules:

- so_number maps to naming_series when available.
- customer_name maps to customer.
- order_date maps to transaction_date.
- delivery_date maps to delivery_date.
- total_amount maps to grand_total when available.
- status maps to status when available.

- external_id should not map to customer.
- external_id should not map to naming_series.
- external_id should not map to name.

- customer_name should NEVER map to customer_name.
- customer_name must map to customer.

- order_date should NEVER map to creation.
- order_date should map to transaction_date.

- delivery_date should map to delivery_date.

Only map fields belonging to Sales Order.

CRITICAL:

- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    elif target_doctype == "Sales Order Item":

        doctype_rules = """
Sales Order Item Rules:

- item_code maps to item_code.
- item_name maps to item_name.
- quantity maps to qty.
- unit_price maps to rate.
- line_total maps to amount.

- item_external_id should only map if an exact ERPNext field exists.
- so_external_id should not map unless an exact ERPNext field exists.

Only map fields belonging to Sales Order Item.

CRITICAL:

- LEFT side MUST be a Unified field.
- RIGHT side MUST be an ERPNext field.
- NEVER reverse the mapping.
"""

    prompt = f"""
You are an ERP migration expert.

Map Unified ERP FIELD NAMES to ERPNext FIELD NAMES.

Entity Type:
{entity_type}

Target ERPNext Doctype:
{target_doctype}

{doctype_rules}

General Rules:

- LEFT side must always be a Unified field name.
- RIGHT side must always be an ERPNext field name.
- NEVER use sample values.
- NEVER use customer names.
- NEVER use addresses.
- NEVER use phone numbers.
- NEVER use emails.
- Map only field names.
- If no suitable ERPNext field exists, omit the mapping.

CRITICAL:

Return ONLY a JSON object.

Valid:

{{
    "email": "email_id"
}}

Valid:

{{
    "customer_name": "customer_name",
    "phone": "mobile_no"
}}

INVALID:

{{
    "customer_name": "Daily Bugle Supplies"
}}

INVALID:

{{
    "city": "New York"
}}

Sample Unified Record:

{json.dumps(sample_record, indent=2, default=str)}

Unified Fields:

{json.dumps(unified_fields, indent=2)}

ERPNext Fields:

{json.dumps(target_fields, indent=2)}
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()

    print(f"TARGET MAPPING ({target_doctype}):")
    print(content)

    matches = re.findall(
        r'\{[\s\S]*?\}',
        content
    )

    if not matches:

        raise Exception(
            f"No JSON found in AI response:\n{content}"
        )

    json_text = matches[-1]

    mapping = json.loads(
        json_text
    )

    # AUTO-ENRICH EXACT MATCHES

    target_lookup = {
        field.lower(): field
        for field in target_fields
    }

    for unified_field in unified_fields:

        if unified_field.lower() in target_lookup:

            if unified_field not in mapping:

                mapping[
                    unified_field
                ] = target_lookup[
                    unified_field.lower()
                ]

    print(
        f"FINAL TARGET MAPPING ({target_doctype}):"
    )

    print(
        json.dumps(
            mapping,
            indent=2
        )
    )

    return mapping

def generate_xero_target_mapping(
    entity_type,
    unified_fields,
    target_fields,
    sample_record
):

    xero_rules = ""

    if entity_type == "items":

        xero_rules = """
Xero Item Rules:

- item_code maps to Code
- item_name maps to Name
- description maps to Description
- sales_price maps to SalesUnitPrice
- purchase_price maps to PurchaseUnitPrice
- is_sold maps to IsSold
- is_purchased maps to IsPurchased

CRITICAL:

- external_id should NEVER map to Code
- external_id should NEVER map to Name

- LEFT side MUST be Unified fields
- RIGHT side MUST be Xero fields

- Never reverse mappings
"""

    elif entity_type == "sales_orders":

        xero_rules = """
Xero Quote Rules:

- so_number maps to QuoteNumber
- customer_name maps to ContactID
- order_date maps to Date
- delivery_date maps to ExpiryDate
- total_amount maps to Total
- status maps to Status

CRITICAL:

- external_id should NEVER map to QuoteNumber
- external_id should NEVER map to ContactID

- LEFT side MUST be Unified fields
- RIGHT side MUST be Xero fields

- Never reverse mappings
"""

    prompt = f"""
You are a Xero integration expert.

Map Unified fields to Xero fields.

Entity Type:
{entity_type}

{xero_rules}

Return ONLY JSON.

Sample Unified Record:

{json.dumps(sample_record, indent=2, default=str)}

Unified Fields:

{json.dumps(unified_fields, indent=2)}

Xero Fields:

{json.dumps(target_fields, indent=2)}
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    matches = re.findall(
        r'\{[\s\S]*?\}',
        content
    )

    if not matches:

        raise Exception(
            f"No JSON found:\n{content}"
        )

    mapping = json.loads(
        matches[-1]
    )

    target_lookup = {
        field.lower(): field
        for field in target_fields
    }

    for unified_field in unified_fields:

        if unified_field.lower() in target_lookup:

            if unified_field not in mapping:

                mapping[
                    unified_field
                ] = target_lookup[
                    unified_field.lower()
                ]

    print(
        "FINAL XERO TARGET MAPPING"
    )

    print(
        json.dumps(
            mapping,
            indent=2
        )
    )

    return mapping

def generate_target_doctypes(
    entity_type,
    unified_fields,
    available_doctypes
):

    prompt = f"""
You are an ERP migration expert.

A Unified ERP entity may need multiple ERPNext doctypes.

Determine which ERPNext doctypes are required
to fully represent this entity.

Entity Type:
{entity_type}

Unified Fields:
{unified_fields}

Available ERPNext Doctypes:
{available_doctypes}

Rules:

- Return only relevant doctypes.
- A customer may require Customer, Contact and Address.
- A supplier may require Supplier, Contact and Address.
- An item typically requires Item.
- An invoice typically requires Sales Invoice.
- A bill typically requires Purchase Invoice.
- Return confidence scores.
- Return ONLY valid JSON.

Example:

[
    {{
        "target_doctype": "Customer",
        "confidence": 1.0
    }},
    {{
        "target_doctype": "Contact",
        "confidence": 0.98
    }}
]

IMPORTANT:

Choose the ERPNext document that best represents the ENTIRE entity.

Do NOT recommend supporting entities that are managed through their own workflows.

Examples:

- Customers should map to Customer.
- Suppliers should map to Supplier.
- Items should map to Item.
- Bills should map to Purchase Invoice.
- Invoices should map to Sales Invoice.
- Purchase Orders should map to Purchase Order.
- Sales Orders should map to Sales Order.

Do NOT recommend:

Customer
Supplier
Contact
Address

unless the entity itself is a customer, supplier, contact, or address.

Return only the primary ERPNext business document(s) that represent the entity.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()

    print("TARGET DISCOVERY RESPONSE:")
    print(content)

    return json.loads(content)

def save_target_mapping(
    tenant_id,
    entity_type,
    target_system,
    mappings
):

    db = SessionLocal()

    try:

        db.execute(
            text("""
                DELETE
                FROM target_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND target_system = :target_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "target_system": target_system
            }
        )

        for target_doctype, data in mappings.items():

            mapping = data["mapping"]

            for unified_field, target_field in mapping.items():

                db.execute(
                    text("""
                        INSERT INTO target_mappings
                        (
                            tenant_id,
                            entity_type,
                            target_system,
                            target_doctype,
                            unified_field,
                            target_field,
                            confidence
                        )
                        VALUES
                        (
                            :tenant_id,
                            :entity_type,
                            :target_system,
                            :target_doctype,
                            :unified_field,
                            :target_field,
                            1.0
                        )
                    """),
                    {
                        "tenant_id":
                            tenant_id,
                        "entity_type":
                            entity_type,
                        "target_system":
                            target_system,
                        "target_doctype":
                            target_doctype,
                        "unified_field":
                            unified_field,
                        "target_field":
                            target_field
                    }
                )

        db.commit()

    finally:
        db.close()

def save_entity_targets(
    tenant_id,
    entity_type,
    target_system,
    targets
):

    db = SessionLocal()

    try:

        db.execute(
            text("""
                DELETE FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND target_system = :target_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "target_system": target_system
            }
        )

        for target in targets:

            db.execute(
                text("""
                    INSERT INTO entity_targets
                    (
                        tenant_id,
                        entity_type,
                        target_system,
                        target_doctype,
                        confidence,
                        approved
                    )
                    VALUES
                    (
                        :tenant_id,
                        :entity_type,
                        :target_system,
                        :target_doctype,
                        :confidence,
                        FALSE
                    )
                """),
                {
                    "tenant_id": tenant_id,

                    "entity_type": entity_type,

                    "target_system": target_system,

                    "target_doctype":
                        target[
                            "target_doctype"
                        ],

                    "confidence":
                        target.get(
                            "confidence",
                            1.0
                        )
                }
            )

        db.commit()

    finally:
        db.close()

def get_entity_targets(
    tenant_id,
    entity_type,
    target_system
):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT
                    target_doctype,
                    confidence,
                    approved
                FROM entity_targets
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND target_system = :target_system
                ORDER BY confidence DESC
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "target_system": target_system
            }
        ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        db.close()

def get_target_mapping_dict(
    tenant_id,
    entity_type,
    target_system,
    target_doctype=None
):

    db = SessionLocal()

    try:

        if target_doctype:

            rows = db.execute(
                text("""
                    SELECT
                        unified_field,
                        target_field
                    FROM target_mappings
                    WHERE
                        tenant_id = :tenant_id
                        AND entity_type = :entity_type
                        AND target_system = :target_system
                        AND target_doctype = :target_doctype
                """),
                {
                    "tenant_id": tenant_id,
                    "entity_type": entity_type,
                    "target_system": target_system,
                    "target_doctype": target_doctype
                }
            ).fetchall()

        else:

            rows = db.execute(
                text("""
                    SELECT
                        unified_field,
                        target_field
                    FROM target_mappings
                    WHERE
                        tenant_id = :tenant_id
                        AND entity_type = :entity_type
                        AND target_system = :target_system
                """),
                {
                    "tenant_id": tenant_id,
                    "entity_type": entity_type,
                    "target_system": target_system
                }
            ).fetchall()

        print("=" * 80)
        print("TARGET MAPPING LOOKUP")
        print("TENANT:", tenant_id)
        print("ENTITY:", entity_type)
        print("TARGET:", target_system)
        print("=" * 80)

        print("ROWS:")
        print(rows)

        return {

            row.unified_field:
            row.target_field

            for row in rows
        }

    finally:
        db.close()



def get_complete_mapping(
    tenant_id,
    entity_type,
    source_system,
    target_system
):

    db = SessionLocal()

    try:

        source_rows = db.execute(
            text("""
                SELECT
                    source_field,
                    destination_field
                FROM field_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND source_system = :source_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "source_system": source_system
            }
        ).fetchall()

        source_to_unified = {}

        for row in source_rows:

            source_to_unified[
                row.source_field
            ] = row.destination_field

        target_rows = db.execute(
            text("""
                SELECT
                    target_doctype,
                    unified_field,
                    target_field
                FROM target_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND target_system = :target_system
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "target_system": target_system
            }
        ).fetchall()

        unified_to_target = {}

        for row in target_rows:

            if row.target_doctype not in unified_to_target:

                unified_to_target[
                    row.target_doctype
                ] = {
                    "mapping": {},
                    "available_fields": []
                }

            unified_to_target[
                row.target_doctype
            ][
                "mapping"
            ][
                row.unified_field
            ] = row.target_field

        for target_doctype in unified_to_target.keys():

            available_fields = (
                get_erpnext_doctype_fields(
                    tenant_id,
                    target_doctype
                )
            )

            unified_to_target[
                target_doctype
            ][
                "available_fields"
            ] = available_fields

        if entity_type == "customers":

            available_unified_fields = [

                "external_id",
                "customer_name",
                "email",
                "phone",
                "address",
                "city",
                "state",
                "country",
                "tax_number",
                "website",
                "status",
                "contact_name",
                "postal_code"
            ]

            unified_field_groups = {

                "Customer": [
                    "customer_name",
                    "website",
                    "tax_number",
                    "status"
                ],

                "Contact": [
                    "contact_name",
                    "email",
                    "phone"
                ],

                "Address": [
                    "address",
                    "city",
                    "state",
                    "country",
                    "postal_code"
                ]
            }

        elif entity_type == "suppliers":

            available_unified_fields = [

                "external_id",
                "supplier_name",
                "email",
                "phone",
                "address",
                "city",
                "state",
                "country",
                "tax_number",
                "website",
                "status",
                "contact_name",
                "postal_code"
            ]

            unified_field_groups = {

                "Supplier": [
                    "supplier_name",
                    "website",
                    "tax_number",
                    "status"
                ],

                "Contact": [
                    "contact_name",
                    "email",
                    "phone"
                ],

                "Address": [
                    "address",
                    "city",
                    "state",
                    "country",
                    "postal_code"
                ]
            }

        elif entity_type == "items":

            available_unified_fields = [

                "external_id",
                "item_code",
                "item_name",
                "description",
                "sales_price",
                "purchase_price",
                "is_inventory",
                "is_sold",
                "is_purchased"
            ]

            unified_field_groups = {

                "Item": [

                    "item_code",
                    "item_name",
                    "description",
                    "sales_price",
                    "purchase_price",
                    "is_inventory",
                    "is_sold",
                    "is_purchased"
                ]
            }

        elif entity_type == "bills":

            available_unified_fields = [

                "external_id",
                "bill_number",
                "supplier_name",
                "bill_date",
                "due_date",
                "subtotal",
                "tax_amount",
                "total_amount",
                "status"
            ]

            unified_field_groups = {

                "Purchase Invoice": [

                    "bill_number",
                    "supplier_name",
                    "bill_date",
                    "due_date",
                    "subtotal",
                    "tax_amount",
                    "total_amount",
                    "status"
                ]
            }

        elif entity_type == "bill_items":

            available_unified_fields = [

                "item_external_id",
                "item_code",
                "item_name",
                "quantity",
                "unit_price",
                "line_total"
            ]

            unified_field_groups = {

                "Purchase Invoice Item": [

                    "item_code",
                    "item_name",
                    "quantity",
                    "unit_price",
                    "line_total"
                ]
            }

        elif entity_type == "invoices":

            available_unified_fields = [

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
            ]

            unified_field_groups = {

                "Invoice": [

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
                ]
            }

        elif entity_type == "invoice_items":

            available_unified_fields = [

                "item_external_id",
                "item_code",
                "item_name",
                "quantity",
                "unit_price",
                "line_total"
            ]

            unified_field_groups = {

                "Invoice Item": [

                    "item_external_id",
                    "item_code",
                    "item_name",
                    "quantity",
                    "unit_price",
                    "line_total"
                ]
            }

        elif entity_type == "purchase_orders":

            available_unified_fields = [

                "external_id",
                "po_number",
                "supplier_name",
                "order_date",
                "delivery_date",
                "total_amount",
                "status"
            ]

            unified_field_groups = {

                "Purchase Order": [

                    "external_id",
                    "po_number",
                    "supplier_name",
                    "order_date",
                    "delivery_date",
                    "total_amount",
                    "status"
                ]
            }

        elif entity_type == "purchase_order_items":

            available_unified_fields = [

                "item_external_id",
                "item_code",
                "item_name",
                "quantity",
                "unit_price",
                "line_total"
            ]

            unified_field_groups = {

                "Purchase Order Item": [

                    "item_external_id",
                    "item_code",
                    "item_name",
                    "quantity",
                    "unit_price",
                    "line_total"
                ]
            }

        elif entity_type == "sales_orders":

            available_unified_fields = [

                "external_id",
                "so_number",
                "customer_name",
                "order_date",
                "delivery_date",
                "total_amount",
                "status"
            ]

            unified_field_groups = {

                "Sales Order": [

                    "external_id",
                    "so_number",
                    "customer_name",
                    "order_date",
                    "delivery_date",
                    "total_amount",
                    "status"
                ]
            }

        elif entity_type == "sales_order_items":

            available_unified_fields = [

                "item_external_id",
                "item_code",
                "item_name",
                "quantity",
                "unit_price",
                "line_total"
            ]

            unified_field_groups = {

                "Sales Order Item": [

                    "item_external_id",
                    "item_code",
                    "item_name",
                    "quantity",
                    "unit_price",
                    "line_total"
                ]
            }

        else:

            available_unified_fields = []

            unified_field_groups = {}

        return {

            "available_unified_fields":
                available_unified_fields,

            "unified_field_groups":
                unified_field_groups,

            "source_to_unified":
                source_to_unified,

            "unified_to_target":
                unified_to_target
        }

    finally:

        db.close()

def get_target_mappings(
    tenant_id,
    entity_type,
    target_system
):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT
                    target_doctype,
                    unified_field,
                    target_field
                FROM target_mappings
                WHERE
                    tenant_id = :tenant_id
                    AND entity_type = :entity_type
                    AND target_system = :target_system
                ORDER BY id
            """),
            {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "target_system": target_system
            }
        ).fetchall()

        mappings = {}

        for row in rows:

            if row.target_doctype not in mappings:

                mappings[
                    row.target_doctype
                ] = {}

            mappings[
                row.target_doctype
            ][
                row.unified_field
            ] = row.target_field

        return mappings

    finally:

        db.close()

def build_payload_from_mapping(
    record,
    mapping
):

    payload = {}

    for unified_field, target_field in mapping.items():

        if not target_field:
            continue

        value = getattr(
            record,
            unified_field,
            None
        )

        if value is None:
            continue

        if str(value).strip() == "":
            continue

        payload[target_field] = value

    return payload