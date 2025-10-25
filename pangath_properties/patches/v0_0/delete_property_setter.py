import frappe

def execute():
    li=["Payment Entry-unit-reqd","Payment Entry-customer-reqd"]
    for i in li:
        if frappe.db.exists("Property Setter",i):
            frappe.delete_doc(
                "Property Setter", i, force=True
            )