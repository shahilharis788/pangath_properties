# Copyright (c) 2022, iterative and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns (filters):
	columns = [
		{
			"fieldname": "property",
			"label": _("Property"),
			"fieldtype": "Link",
			"options": "Property",
			"width": "150"
		},
		{
			"fieldname": "available",
			"label": _("Available"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "booked",
			"label": _("Booked"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "leased",
			"label": _("Leased"),
			"fieldtype": "Data",
			"width": "150"
		},
			{
			"fieldname": "sold",
			"label": _("Sold"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "not_hand_over",
			"label": _("Not Hand Over"),
			"fieldtype": "Data",
			"width": "150"
		},
	]
	return columns

def get_data (filters):
	query = f"""
		SELECT
			b.name AS property,
			count(CASE WHEN u.status='Available' THEN 1 END) as available,
			count(CASE WHEN u.status='Booked' THEN 1 END) as booked,
			count(CASE WHEN u.status='Leased' THEN 1 END) as leased,
			count(CASE WHEN u.status='Sold' THEN 1 END) as sold,
			count(CASE WHEN u.status='Not Hand Over' THEN 1 END) as not_hand_over
		FROM
			`tabProperty` AS b LEFT JOIN
			`tabUnit` AS u ON u.property=b.name
		WHERE
			u.property IS NOT NULL
	"""
	if filters.get('property'):
		query = f"{query} AND b.name='{filters.get('property')}'"
	query = f"{query} GROUP BY b.name"
	data = frappe.db.sql(f"{query}", as_dict=True)
	return data