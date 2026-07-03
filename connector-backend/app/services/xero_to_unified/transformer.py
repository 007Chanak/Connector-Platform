from groq import Groq
import os
import json
import re
from sqlalchemy import text
from datetime import datetime
from app.database import SessionLocal


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def transform_customer_using_mapping(
    contact,
    mapping
):

    unified_customer = {}

    for source_field, destination_field in mapping.items():
        if source_field == "Phones":
            phone = ""
            for p in contact.get(
                "Phones",
                []
            ):
                if p.get(
                    "PhoneNumber"
                ):
                    phone = p.get(
                        "PhoneNumber"
                    )
                    break

            unified_customer[
                destination_field
            ] = phone

        elif source_field == "Addresses":

            address = ""
            city = ""
            state = ""
            country = ""

            addresses = contact.get(
                "Addresses",
                []
            )

            if len(addresses) > 1:

                addr = addresses[1]

                address = addr.get(
                    "AddressLine1",
                    ""
                )

                city = addr.get(
                    "City",
                    ""
                )

                state = addr.get(
                    "Region",
                    ""
                )

                country = addr.get(
                    "Country",
                    ""
                )

            unified_customer[
                destination_field
            ] = address

            unified_customer[
                "city"
            ] = city

            unified_customer[
                "state"
            ] = state

            unified_customer[
                "country"
            ] = country

        elif source_field == "PostalCode":
            postal_code = ""
            for addr in contact.get(
                "Addresses",
                []
            ):
                if addr.get(
                    "PostalCode"
                ):
                    postal_code = addr.get(
                        "PostalCode"
                    )
                    break

            unified_customer[
                destination_field
            ] = postal_code

        elif source_field == "ContactPersons":
            contact_name = ""
            persons = contact.get(
                "ContactPersons",
                []
            )
            if persons:
                first = persons[0].get(
                    "FirstName",
                    ""
                )
                last = persons[0].get(
                    "LastName",
                    ""
                )
                contact_name = (
                    first + " " + last
                ).strip()
            else:
                first = contact.get(
                    "FirstName",
                    ""
                )
                last = contact.get(
                    "LastName",
                    ""
                )
                contact_name = (
                    first + " " + last
                ).strip()
            unified_customer[
                destination_field
            ] = contact_name
        else:
            unified_customer[
                destination_field
            ] = contact.get(
                source_field
            )
    return unified_customer

def transform_supplier_using_mapping(
    supplier,
    mapping
):
    unified_supplier = {}

    for source_field, destination_field in mapping.items():
        if source_field == "Phones":
            phone = ""
            for p in supplier.get(
                "Phones",
                []
            ):
                if p.get(
                    "PhoneNumber"
                ):
                    phone = p.get(
                        "PhoneNumber"
                    )
                    break

            unified_supplier[
                destination_field
            ] = phone

        elif source_field == "Addresses":

            address = ""
            city = ""
            state = ""
            country = ""

            addresses = supplier.get(
                "Addresses",
                []
            )

            for addr in addresses:

                if addr.get(
                    "AddressLine1"
                ):

                    address = addr.get(
                        "AddressLine1",
                        ""
                    )

                    city = addr.get(
                        "City",
                        ""
                    )

                    state = addr.get(
                        "Region",
                        ""
                    )

                    country = addr.get(
                        "Country",
                        ""
                    )

                    break

            unified_supplier[
                destination_field
            ] = address

            unified_supplier[
                "city"
            ] = city

            unified_supplier[
                "state"
            ] = state

            unified_supplier[
                "country"
            ] = country

        elif source_field == "PostalCode":
            postal_code = ""
            for addr in supplier.get(
                "Addresses",
                []
            ):
                if addr.get(
                    "PostalCode"
                ):
                    postal_code = addr.get(
                        "PostalCode"
                    )
                    break

            unified_supplier[
                destination_field
            ] = postal_code

        elif source_field == "ContactPersons":
            contact_name = ""
            persons = supplier.get(
                "ContactPersons",
                []
            )
            if persons:
                first = persons[0].get(
                    "FirstName",
                    ""
                )
                last = persons[0].get(
                    "LastName",
                    ""
                )
                contact_name = (
                    first + " " + last
                ).strip()
            else:
                first = supplier.get(
                    "FirstName",
                    ""
                )
                last = supplier.get(
                    "LastName",
                    ""
                )
                contact_name = (
                    first + " " + last
                ).strip()
            unified_supplier[
                destination_field
            ] = contact_name

        elif source_field == "FirstName":

            first = supplier.get(
                "FirstName",
                ""
            )

            last = supplier.get(
                "LastName",
                ""
            )

            unified_supplier[
                destination_field
            ] = (
                first + " " + last
            ).strip()

        elif source_field == "LastName":

            continue
        else:
            unified_supplier[
                destination_field
            ] = supplier.get(
                source_field
            )
    return unified_supplier

def transform_item_using_mapping(
    item,
    mapping
):

    unified_item = {}

    for source_field, destination_field in mapping.items():

        if source_field == "SalesDetails.UnitPrice":

            unified_item[
                destination_field
            ] = (
                item.get(
                    "SalesDetails",
                    {}
                ).get(
                    "UnitPrice"
                )
            )

        elif source_field == "PurchaseDetails.UnitPrice":

            unified_item[
                destination_field
            ] = (
                item.get(
                    "PurchaseDetails",
                    {}
                ).get(
                    "UnitPrice"
                )
            )

        else:

            unified_item[
                destination_field
            ] = item.get(
                source_field
            )

    return unified_item


def xero_date_to_iso(date_str):

    if not date_str:
        return None

    match = re.search(
        r"/Date\((\d+)",
        str(date_str)
    )

    if not match:
        return date_str

    timestamp_ms = int(
        match.group(1)
    )

    return datetime.utcfromtimestamp(
        timestamp_ms / 1000
    ).date()


def transform_invoice_using_mapping(
    invoice,
    mapping
):

    unified_invoice = {}

    for source_field, destination_field in mapping.items():
        if source_field == "Contact.Name":
            unified_invoice[
                destination_field
            ] = invoice.get(
                "Contact",
                {}
            ).get(
                "Name"
            )

        elif source_field in [
            "Date",
            "DueDate"
        ]:
            unified_invoice[
                destination_field
            ] = xero_date_to_iso(
                invoice.get(
                    source_field
                )
            )

        else:
            unified_invoice[
                destination_field
            ] = invoice.get(
                source_field
            )

    return unified_invoice

def transform_invoice_item_using_mapping(
    line_item,
    invoice_external_id,
    mapping
):

    unified_item = {}

    for source_field, destination_field in mapping.items():

        if source_field == "Item.ItemID":

            unified_item[
                destination_field
            ] = (
                line_item
                .get("Item", {})
                .get("ItemID")
            )

        else:

            unified_item[
                destination_field
            ] = line_item.get(
                source_field
            )

    unified_item[
        "invoice_external_id"
    ] = invoice_external_id

    return unified_item

def transform_bill_using_mapping(
    bill,
    mapping
):

    unified_bill = {}

    for source_field, destination_field in mapping.items():

        if source_field == "Contact.Name":

            unified_bill[
                destination_field
            ] = bill.get(
                "Contact",
                {}
            ).get(
                "Name"
            )

        elif source_field in [
            "Date",
            "DueDate"
        ]:

            unified_bill[
                destination_field
            ] = xero_date_to_iso(
                bill.get(
                    source_field
                )
            )

        else:

            unified_bill[
                destination_field
            ] = bill.get(
                source_field
            )

    return unified_bill

def transform_bill_item_using_mapping(
    line_item,
    bill_external_id,
    mapping
):

    unified_item = {}

    for source_field, destination_field in mapping.items():

        if source_field == "Item.ItemID":

            unified_item[
                destination_field
            ] = (
                line_item
                .get("Item", {})
                .get("ItemID")
            )

        else:

            unified_item[
                destination_field
            ] = line_item.get(
                source_field
            )

    unified_item[
        "bill_external_id"
    ] = bill_external_id

    return unified_item


def transform_sales_order_using_mapping(
    sales_order,
    mapping
):

    unified_so = {}

    for source_field, destination_field in mapping.items():

        if source_field == "Contact.Name":

            unified_so[
                destination_field
            ] = sales_order.get(
                "Contact",
                {}
            ).get(
                "Name"
            )

        elif source_field in [

            "Date",

            "ExpiryDate"
        ]:

            unified_so[
                destination_field
            ] = xero_date_to_iso(
                sales_order.get(
                    source_field
                )
            )

        else:

            unified_so[
                destination_field
            ] = sales_order.get(
                source_field
            )

    return unified_so

def transform_sales_order_item_using_mapping(
    sales_order_item,
    mapping
):

    transformed = {}

    for source_field, destination_field in mapping.items():

        value = None

        if source_field == "LineItemID":

            value = sales_order_item.get(
                "LineItemID"
            )

        elif source_field == "Item.ItemID":

            value = sales_order_item.get(
                "LineItemID"
            )

        elif "." in source_field:

            parts = source_field.split(".")

            current = sales_order_item

            for part in parts:

                if isinstance(current, dict):

                    current = current.get(part)

                else:

                    current = None
                    break

            value = current

        else:

            value = sales_order_item.get(
                source_field
            )

        transformed[
            destination_field
        ] = value

    return transformed

def transform_purchase_order_using_mapping(
    purchase_order,
    mapping
):

    unified_po = {}

    for (
        source_field,
        destination_field
    ) in mapping.items():
        if source_field == "Contact.Name":
            unified_po[
                destination_field
            ] = purchase_order.get(
                "Contact",
                {}
            ).get(
                "Name"
            )

        elif source_field in [
            "Date",
            "DeliveryDate"

        ]:
            unified_po[
                destination_field
            ] = xero_date_to_iso(
                purchase_order.get(
                    source_field
                )
            )

        else:
            unified_po[
                destination_field
            ] = purchase_order.get(
                source_field
            )

    return unified_po

def transform_purchase_order_item_using_mapping(

    line_item,
    po_external_id,
    mapping

):

    unified_item = {}

    for source_field, destination_field in mapping.items():

        if source_field == "Item.ItemID":

            unified_item[
                destination_field
            ] = (
                line_item
                .get("Item", {})
                .get("ItemID")
            )

        else:

            unified_item[
                destination_field
            ] = line_item.get(
                source_field
            )

    unified_item[
        "po_external_id"
    ] = po_external_id

    return unified_item

def transform_account_using_mapping(
    account,
    mapping
):

    unified_account = {}

    for source_field, destination_field in mapping.items():

        unified_account[
            destination_field
        ] = account.get(
            source_field
        )

    return unified_account