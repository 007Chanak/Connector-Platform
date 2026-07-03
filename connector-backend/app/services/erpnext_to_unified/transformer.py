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

def transform_erpnext_customer_using_mapping(
    customer,
    mapping
):

    transformed = {}

    for source_field, unified_field in mapping.items():

        value = customer.get(
            source_field
        )

        transformed[
            unified_field
        ] = value

    return transformed

def transform_erpnext_supplier_using_mapping(
    supplier,
    mapping
):

    transformed = {}

    for source_field, destination_field in mapping.items():

        value = supplier.get(
            source_field
        )

        transformed[
            destination_field
        ] = value

    return transformed

def transform_erpnext_item_using_mapping(
    item,
    mapping
):

    transformed = {}

    for source_field, destination_field in mapping.items():

        value = item.get(
            source_field
        )

        transformed[
            destination_field
        ] = value

    return transformed

def transform_erpnext_sales_order_using_mapping(
    sales_order,
    mapping
):

    transformed = {}

    for unified_field, erpnext_field in mapping.items():

        if not erpnext_field:
            continue

        transformed[
            unified_field
        ] = sales_order.get(
            erpnext_field
        )

    print("=" * 80)
    print("TRANSFORMED SALES ORDER")
    print(transformed)
    print("=" * 80)

    return transformed


def transform_erpnext_sales_order_item_using_mapping(
    item,
    mapping
):

    transformed = {}

    for source_field, destination_field in mapping.items():

        if not destination_field:
            continue

        transformed[
            destination_field
        ] = item.get(
            source_field
        )

    print("=" * 80)
    print("TRANSFORMED SALES ORDER ITEM")
    print(transformed)
    print("=" * 80)

    return transformed