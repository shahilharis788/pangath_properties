import frappe
from erpnext.maintenance.doctype.maintenance_visit.maintenance_visit import MaintenanceVisit

@frappe.whitelist()
def create_material_request(doc):
    main_vis=frappe.get_doc("Maintenance Visit",doc)
    met_doc=frappe.new_doc("Material Request")
    met_doc.company=main_vis.company
    met_doc.custom_maintenance_visit=main_vis.name
    for i in main_vis.purposes:
        met_doc.append("items", {
			"item_code":i.item_code,})
    return met_doc

@frappe.whitelist()
def create_sales_invoice(doc):
    main_vis=frappe.get_doc("Maintenance Visit",doc)
    sale_doc=frappe.new_doc("Sales Invoice")
    sale_doc.company=main_vis.company
    sale_doc.customer=main_vis.customer
    sale_doc.property=main_vis.custom_property
    sale_doc.unit=main_vis.custom_unit
    sale_doc.custom_maintenance_visit=main_vis.name
    for i in main_vis.purposes:
        sale_doc.append("items",{
            "item_code":i.item_code
        }
        )
    return sale_doc



@frappe.whitelist()
def create_material_issue(doc):
    main_vis=frappe.get_doc("Maintenance Visit",doc)
    sale_doc=frappe.new_doc("Stock Entry")
    sale_doc.company=main_vis.company
    sale_doc.customer=main_vis.customer
    sale_doc.stock_entry_type = "Material Issue"
    sale_doc.custom_maintenance_visit = main_vis.name
    for i in main_vis.purposes:
        sale_doc.append("items",{
            "item_code":i.item_code
        }
        )
    return sale_doc





class CustomMaintenanceVisit(MaintenanceVisit):
    def validate_purpose_table(self):
        pass


def change_status(doc,method):
    if doc.maintenance_schedule:
        maintenance_schedule = frappe.get_doc("Maintenance Schedule",doc.maintenance_schedule)
        frappe.db.set_value("Issue",maintenance_schedule.issue,"status","Resolved")
