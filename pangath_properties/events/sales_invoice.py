import frappe

def set_tax_template(doc, method=None):
    if not doc.custom_tenancy_contract:
        return
    charges_tax = frappe.db.get_all("Type Of Charges", {"parent": doc.custom_tenancy_contract}, pluck = "particulars")
    for row in doc.items:
        tax = frappe.db.get_value("Unit Details", {"parent": doc.custom_tenancy_contract, "unit":row.item_code}, "tax_template")
        row.item_tax_template = tax
        if row.item_code in charges_tax:
            tax = frappe.db.get_value("Type Of Charges", {"parent": doc.custom_tenancy_contract, "particulars":row.item_code}, "item_tax_template")
            row.item_tax_template = tax