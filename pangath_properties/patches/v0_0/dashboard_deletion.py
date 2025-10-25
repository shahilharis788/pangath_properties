
import frappe

def execute():

    conditions = {
        "module": ("=", "Pangath Properties")
    }

    dashboards = frappe.get_all("Dashboard", filters=conditions, fields=["name", "module"])

    if dashboards:
        for dashboard in dashboards:
            frappe.delete_doc("Dashboard", dashboard.name, ignore_permissions=True, force=True)
        
        print("Data deletion completed.")
    else:
        print("No dashboards found based on the specified conditions.")
