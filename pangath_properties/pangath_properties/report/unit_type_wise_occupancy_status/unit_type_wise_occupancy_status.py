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
			"fieldname": "unit_type",
			"label": _("Unit Type"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "no_unit",
			"label": _("No. Unit"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "rented",
			"label": _("Rented"),
			"fieldtype": "Data",
			"width": "150"
		},
			{
			"fieldname": "vacant",
			"label": _("Vacant"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "reserved",
			"label": _("Reserved"),
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "rent",
			"label": _("Rental value"),
			"fieldtype": "Data",
			"width": "150"
		},
	]
	return columns

def get_data (filters):
	query = f"""
		SELECT
			b.name AS property,u.unit_type as unit_type,
			count(u.unit_type) AS no_unit,
			count(CASE WHEN u.status='Booked' THEN 1 END) as reserved,
      		count(CASE WHEN u.status='Leased' THEN 1 END) as rented,
			count(CASE WHEN u.status='Available' THEN 1 END) as vacant,
			sum(u.rent) AS rent
		FROM
			`tabProperty` AS b LEFT JOIN
			`tabUnit` AS u ON u.property=b.name
		WHERE
			u.property IS NOT NULL
		GROUP BY 
			u.unit_type,b.name

		ORDER BY 
    		b.name;		
	"""
	if filters.get('property'):
		query = f"{query} AND b.name='{filters.get('property')}'"
	data = frappe.db.sql(f"{query}", as_dict=True)
	return data