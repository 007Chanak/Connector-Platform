def transform_erpnext_item(item):

    return {

        "source": "erpnext",

        "external_id":
            item.get("name"),

        "item_code":
            item.get("item_code"),

        "item_name":
            item.get("item_name"),

        "description":
            item.get("description"),

        "unit_price":
            item.get("standard_rate"),

        "currency":
            "INR",

        "status":
            "Active"
    }


def transform_xero_item(item):

    sales_details = item.get(
        "SalesDetails",
        {}
    )

    return {

        "source": "xero",

        "external_id":
            item.get("ItemID"),

        "item_code":
            item.get("Code"),

        "item_name":
            item.get("Name"),

        "description":
            item.get("Description"),

        "unit_price":
            sales_details.get(
                "UnitPrice"
            ),

        "currency":
            "INR",

        "status":
            item.get("Status")
    }