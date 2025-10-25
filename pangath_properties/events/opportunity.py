import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def schedule_site_visit(source_name, target_doc=None):
    if source_name:
        def set_missing_values(source, target):
            target.run_method("set_missing_values")
        doclist = get_mapped_doc("Opportunity", source_name, {
            "Opportunity": {
                "doctype": "Site Visit Schedule",
                "field_map": {
                    "customer_name": "visitors_full_name",
                    "contact_mobile": "contact",
                    "contact_email": "email_id",
                    "whatsapp": "whatsapp",
                    "phone": "phone",
                    "name":"opportunity"
                }
            }
        }, target_doc, set_missing_values)
        return doclist



@frappe.whitelist()
def create_tenancy_application(source_name, target_doc=None):
    if source_name:
        def set_missing_values(source, target):
            target.run_method("set_missing_values")
        doclist = get_mapped_doc("Opportunity", source_name, {
            "Opportunity": {
                "doctype": "Tenancy Application",
                "field_map": {
                    # "customer_name": "visitors_full_name",
                    "contact_mobile": "contact_no",
                    "contact_email": "email",
                    # "whatsapp": "whatsapp",
                    "contact_person": "tenant_name",
                    "name":"opportunity"
                }
            }
        }, target_doc, set_missing_values)
        return doclist