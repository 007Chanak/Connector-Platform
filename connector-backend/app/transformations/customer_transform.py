def transform_xero_contact(contact):

    phone = ""

    phones = contact.get("Phones", [])

    for p in phones:
        if p.get("PhoneNumber"):
            phone = p.get("PhoneNumber")
            break

    address = ""

    address = ""

    address_obj = None

    postal_code = ""

    for addr in contact.get("Addresses", []):

        if (
            addr.get("AddressLine1")
            or addr.get("City")
            or addr.get("Region")
            or addr.get("Country")
        ):
            address_obj = addr
            break

    if address_obj:

        postal_code = (
            address_obj.get("PostalCode")
            or ""
        )

        address_parts = []

        if address_obj.get("AddressLine1"):
            address_parts.append(
                address_obj["AddressLine1"]
            )

        if address_obj.get("City"):
            address_parts.append(
                address_obj["City"]
            )

        if address_obj.get("Region"):
            address_parts.append(
                address_obj["Region"]
            )

        if address_obj.get("Country"):
            address_parts.append(
                address_obj["Country"]
            )

        address = ", ".join(address_parts)

    print("CONTACT PERSONS:", contact.get("ContactPersons"))

    contact_name = " ".join(
        filter(
            None,
            [
                contact.get("FirstName"),
                contact.get("LastName")
            ]
        )
    )

    if not contact_name:
        contact_name = contact.get("Name", "")

    print(
        "POSTAL DEBUG:",
        contact.get("Name"),
        postal_code
    )

    return {

        "external_id": contact.get("ContactID"),

        "customer_name": contact.get("Name"),

        "contact_name": contact_name,

        "email": contact.get("EmailAddress"),

        "phone": phone,

        "address": address,

        "tax_number": contact.get("TaxNumber"),

        "website": contact.get("Website"),

        "status": contact.get("ContactStatus"),

        "postal_code": postal_code,

        "created_at": None,

        "source": "xero"
    }