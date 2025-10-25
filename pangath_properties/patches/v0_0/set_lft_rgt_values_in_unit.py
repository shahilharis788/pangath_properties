import frappe

def execute():
    units = frappe.db.get_all("Unit", filters={}, order_by="creation desc", pluck="name")
    rgt = (len(units)*2) - 1
    lft = rgt-1
    for i in units:
        if i == "Unit":
            frappe.db.set_value("Unit", i, {"lft": 1, "rgt": (len(units) * 2)})
        else:
            frappe.db.set_value("Unit", i, {"lft": lft, "rgt": rgt})
            rgt = lft - 1
            lft = rgt - 1