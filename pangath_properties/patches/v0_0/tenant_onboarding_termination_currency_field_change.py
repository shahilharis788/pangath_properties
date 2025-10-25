
import frappe

def execute():
    '''
    data fields were changed to currency
    '''
    fields = ["total_refundable", "refund_pdc", "refund_cleared"]
    meta = frappe.get_meta("Tenant Onboarding Termination")

    for field in fields:
        if not meta.has_field(field):
            return

        tenant_onb_terms = frappe.get_all("Tenant Onboarding Termination", filters={field: ["in", [None]]}, fields=["name"])
        for tenant in tenant_onb_terms:
            frappe.db.set_value("Tenant Onboarding Termination", tenant.get("name"), field, 0)  