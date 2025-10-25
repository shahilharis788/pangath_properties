import frappe

def after_install():
    type_list = ["Customer", "Unit", "Property"]
    for type in type_list:
        if not frappe.db.exists("Accounting Dimension", type):
            accounting_dimension = frappe.new_doc("Accounting Dimension")
            accounting_dimension.name = type
            accounting_dimension.document_type = type
            accounting_dimension.insert(ignore_permissions=True)
