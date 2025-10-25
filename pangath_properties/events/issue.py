import frappe

@frappe.whitelist()
def create_maintenance_schedule(doc):
    issue_doc=frappe.get_doc("Issue",doc)
    main_doc=frappe.new_doc("Maintenance Schedule")
    main_doc.customer=issue_doc.customer
    main_doc.custom_tenancy_contract=issue_doc.custom_tenancy_contract
    main_doc.custom_property=issue_doc.property
    main_doc.custom_unit_no=issue_doc.unit
    main_doc.issue=issue_doc.name
    if issue_doc.custom_tenancy_contract:
        main_doc.company=frappe.db.get_value("Tenancy Contract",issue_doc.custom_tenancy_contract,"company")
    if main_doc:
        return main_doc



def validate(doc,method):
    doc.subject = str(doc.unit) + "-" + str(doc.issue_type) + "-" + str(doc.custom_request_date)