import frappe
from frappe import _

@frappe.whitelist()
def get_properties():
	return frappe.db.sql(
		"""
		select
			name, image
		from
			tabProperty
		""", as_dict=1)
