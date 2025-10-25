import frappe
from frappe import _

@frappe.whitelist()
def get_buildings():
	return frappe.db.sql(
		"""
		select
			name, image
		from
			tabBuilding
		""", as_dict=1)
