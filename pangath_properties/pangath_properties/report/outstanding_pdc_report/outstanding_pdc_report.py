# Copyright (c) 2023, iterative and contributors
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
			"fieldname": "name",
			"label": _("Name"),
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": "200"
		},
		{
			"fieldname": "party",
			"label": _("Party"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "150"
		},
		{
			"fieldname": "paid_to",
			"label": _("Paid To"),
			"fieldtype": "Link",
			"options": "Account",
			"width": "100"
		},
		{
			"fieldname": "paid_from",
			"label": _("Paid From"),
			"fieldtype": "Link",
			"options": "Account",
			"width": "100"
		},
		{
			"fieldname": "payment_type",
			"label": _("Payment Type"),
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "tenant_onboarding",
			"label": _("Tenant Onboarding"),
			"fieldtype": "Link",
			"options": "Tenant Onboarding",
			"width": "150"
		},
		{
			"fieldname": "journal_entry",
			"label": _("Journal Entry"),
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": "150"
		},
		{
			"fieldname": "reference_date",
			"label": _("Reference Date"),
			"fieldtype": "Date",
			"width": "125"
		},
		{
			"fieldname": "reference_no",
			"label": _("Reference No"),
			"fieldtype": "Data",
			"width": "125"
		},
		{
			"fieldname": "paid_amount",
			"label": _("Amount"),
			"fieldtype": "Amount",
			"width": "150"
		},
	]
	return columns

def get_data (filters):
	query = f"""
		SELECT
			pe.name as name,
			pe.paid_to as paid_to,
			pe.paid_from as paid_from,
			pe.reference_no as reference_no,
			pe.tenant_onboarding as tenant_onboarding,
			pe.journal_entry as journal_entry,
			pe.cheque_issue_date as cheque_issue_date,
			pe.reference_date as reference_date,
			pe.paid_amount as paid_amount, 
			pe.party as party,
			pe.payment_type,
			pe.reference_no
		FROM
			`tabPayment Entry` AS pe
		WHERE
			pe.payment_type IN ("Receive", "Pay") AND
			pe.is_pdc = 1 AND
			pe.docstatus = 1 AND
			pe.status_je != "Bounce Cheque" AND
			pe.status_je != "Hold" AND
			pe.clearance_date IS NULL AND
			pe.reference_date IS NOT NULL
		
	"""
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	if from_date and to_date:
		query = f"{query} AND pe.reference_date BETWEEN '{from_date}' AND '{to_date}'"
	if filters.get('tenant_onboarding'):
		query = f"{query} AND pe.tenant_onboarding ='{filters.get('tenant_onboarding')}'"
	if filters.get('customer'):
		query = f"{query} AND pe.party ='{filters.get('customer')}'"

	query = f"{query} ORDER BY pe.reference_date ASC"
	# if filters.get('unit'):
	# 	query = f"{query} AND u.name='{filters.get('unit')}'"
	data = frappe.db.sql(f"{query}", as_dict=True)

	return data