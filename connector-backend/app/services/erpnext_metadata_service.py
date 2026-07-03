import requests

from sqlalchemy import text

from app.database import SessionLocal


def get_erpnext_doctype_fields(
    tenant_id,
    doctype
):

    db = SessionLocal()

    try:

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

        if not erp:

            return []

        headers = {
            "Authorization":
                f"token {erp.api_key}:{erp.api_secret}"
        }

        response = requests.get(
            (
                f"{erp.erp_url}"
                "/api/method/"
                "frappe.desk.form.load.getdoctype"
                f"?doctype={doctype}"
            ),
            headers=headers
        )

        data = response.json()

        fields = []

        docs = data.get(
            "docs",
            []
        )

        if not docs:

            return []

        meta = docs[0]

        ignored_fieldtypes = {

            "Section Break",
            "Column Break",
            "Tab Break",
            "HTML",
            "Button",
            "Fold",
            "Heading"
        }

        ignored_fieldnames = {

            "amended_from",
            "owner",
            "creation",
            "modified",
            "modified_by",
            "idx",
            "docstatus",
            "_user_tags",
            "_comments",
            "_assign",
            "_liked_by"
        }

        for field in meta.get(
            "fields",
            []
        ):

            fieldname = field.get(
                "fieldname"
            )

            fieldtype = field.get(
                "fieldtype"
            )

            hidden = field.get(
                "hidden",
                0
            )

            if not fieldname:

                continue

            if fieldtype in ignored_fieldtypes:

                continue

            if fieldname in ignored_fieldnames:

                continue

            if hidden:

                continue

            fields.append(
                fieldname
            )

        return sorted(
            list(set(fields))
        )

    finally:

        db.close()