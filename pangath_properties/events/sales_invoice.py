import frappe

def set_tax_template(doc, method=None):
    if not doc.custom_tenancy_contract:
        return
    item_tax = frappe.db.get_value("TA Payment Schedule", {"parent": doc.custom_tenancy_contract}, "item_tax_template")
    charges_tax = frappe.db.get_all("Type Of Charges", {"parent": doc.custom_tenancy_contract}, pluck = "item_tax_template")
    charge_index = 0
    if item_tax or charges_tax:
        for idx, item in enumerate(doc.items):
            if item.description == "Rent": # rent is description for rent item only
                item.item_tax_template = item_tax
            else: # for charges
                if charges_tax and len(charges_tax) <= charge_index + 1:
                    item.item_tax_template = charges_tax[charge_index]
                    