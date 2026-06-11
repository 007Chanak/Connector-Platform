def transform_xero_invoice(invoice):

    return {

        "source": "xero",

        "external_id":
            invoice.get("InvoiceID"),

        "invoice_number":
            invoice.get("InvoiceNumber"),

        "customer_name":
            invoice.get(
                "Contact",
                {}
            ).get("Name"),

        "invoice_date":
            invoice.get("DateString"),

        "due_date":
            invoice.get("DueDateString"),

        "subtotal":
            invoice.get("SubTotal"),

        "tax_amount":
            invoice.get("TotalTax"),

        "total_amount":
            invoice.get("Total"),

        "currency":
            invoice.get("CurrencyCode"),

        "status":
            invoice.get("Status")
    }


def transform_erpnext_invoice(invoice):

    return {

        "source": "erpnext",

        "external_id":
            invoice.get("name"),

        "invoice_number":
            invoice.get("name"),

        "customer_name":
            invoice.get("customer_name"),

        "invoice_date":
            invoice.get("posting_date"),

        "due_date":
            invoice.get("due_date"),

        "subtotal":
            invoice.get("net_total"),

        "tax_amount":
            invoice.get(
                "total_taxes_and_charges"
            ),

        "total_amount":
            invoice.get(
                "grand_total"
            ),

        "currency":
            invoice.get("currency"),

        "status":
            invoice.get("status")
    }