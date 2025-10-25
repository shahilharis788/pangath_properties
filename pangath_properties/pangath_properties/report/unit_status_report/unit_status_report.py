# Copyright (c) 2023, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(filters, columns, data)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary



def get_columns(filters):
    columns = [
        {
            "fieldname": "unit_company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": "250",
            "align": "Left"
        },
        {
            "fieldname": "unit_property",
            "label": _("Property Name"),
            "fieldtype": "Link",
            "options": "Property",
            "width": "200",
            "align": "Left"
        },
        {
            "fieldname": "unit_name",
            "label": _("Unit Name"),
            "fieldtype": "Data",
            "width": "150",
            "align": "Left"
        },
        {
            "fieldname": "unit_apartment",
            "label": _("Apartment Type"),
            "fieldtype": "Link",
            "options": "Apartment Type",
            "width": "150",
            "align": "Left"
        },
        {
            "fieldname": "unit_nature",
            "label": _("Unit Nature"),
            "fieldtype": "Data",
            "width": "150"
        },
        {
            "fieldname": "unit_type",
            "label": _("Unit Type"),
            "fieldtype": "Data",
            "width": "150",
            "align": "Left"
        },
        {
            "fieldname": "unit_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": "150",
            "align": "Left"
        }
    ]
    return columns



def get_data (filters):
	query = f"""
		SELECT
			unit.company as unit_company,
			unit.property as unit_property,
			unit.unit_name as unit_name,
			IFNULL(unit.apartment_type, '') as unit_apartment,
			unit.unit_nature as unit_nature,
			IFNULL(unit.unit_type, '') as unit_type,
			unit.status as unit_status
		FROM
			`tabUnit` AS unit
		WHERE
			unit.status is NOT NULL
	"""
	if filters.get('status'):
		status_values = filters.get('status')
		status_values = ["'" + status + "'" for status in status_values]
		status_str = ', '.join(status_values)
		query = f"{query} AND unit.status IN ({status_str})"
	if filters.get('property'):
		query = f"{query} AND unit.property='{filters.get('property')}'"
	if filters.get('company'):
		query = f"{query} AND unit.company='{filters.get('company')}'"
	if filters.get('unit_name'):
		query = f"{query} AND unit.unit_name='{filters.get('unit_name')}'"
	if filters.get('unit_type'):
		query = f"{query} AND unit.unit_type='{filters.get('unit_type')}'"

	data= frappe.db.sql(query, as_dict=True)
	return data


def get_report_summary(data):
    status_counts = {}
    for row in data:
        status = row.get('unit_status')
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    report_summary = []
    for status, count in status_counts.items():
        report_summary.append({
            "value": count,
            "label": status,
            "datatype": "Int",
            "currency": None,
        })
    return report_summary

def get_chart_data(filters, columns, data):
    labels = [d.get("label") for d in columns]
    status_counts = {}
    for row in data:
        status = row.get('unit_status')
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    datasets = [{"name": "Status", "values": list(status_counts.values())}]
    chart = {"data": {"labels": list(status_counts.keys()), "datasets": datasets}}
    if not filters.accumulated_values:
        chart["type"] = "pie" 
    else:
        chart["type"] = "line"
    return chart

