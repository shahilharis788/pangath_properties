from frappe import _


def get_data():
    return {
        "fieldname": "unit",
        "non_standard_fieldnames": {
            "Tenancy Contract": "unit_number",
        },
        "transactions": [
            {"label": _(""), "items": ["Tenant Onboarding", "Tenancy Contract"]},
            {"label": _(""), "items": ["Payment Entry", "Journal Entry"]},
            {"label": _(""), "items": ["Tenant Onboarding Termination"]}
        ]
    }