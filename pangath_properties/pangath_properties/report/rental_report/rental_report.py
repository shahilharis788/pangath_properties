# Copyright (c) 2025, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{
			"label": _("Contract Name"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Tenancy Contract",
			"width": 150
		},
		{
			"label": _("Property Name"),
			"fieldname": "property_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Period Start Date"),
			"fieldname": "period_start_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Period End Date"),
			"fieldname": "period_end_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Unit Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Rental Amount"),
			"fieldname": "rental_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Admin Fee"),
			"fieldname": "admin_fee",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("VAT"),
			"fieldname": "vat",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Installment"),
			"fieldname": "installment",
			"fieldtype": "Int",
			"width": 100
		},
		# {
		# 	"label": _("Cheque No / Payment Mode"),
		# 	"fieldname": "chq_no",
		# 	"fieldtype": "Data",
		# 	"width": 150
		# },
		{
			"label": _("Periodic Payment AmountS"),
			"fieldname": "payment_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Payment Schedule Date"),
			"fieldname": "payment_scheduled_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Paid Amount"),
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Security Cash"),
			"fieldname": "sec_dep_cash",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Security Cheque"),
			"fieldname": "sec_dep_chq",
			"fieldtype": "Currency",
			"width": 120
		}
	]
	return columns

def get_data(filters=None):
	conditions = []
	params = {}

	if filters:
		if filters.get("contract_name"):
			conditions.append("tc.name = %(contract_name)s")
			params["contract_name"] = filters["contract_name"]
		if filters.get("property_name"):
			conditions.append("tc.property_name = %(property_name)s")
			params["property_name"] = filters["property_name"]

	where_clause = ""
	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)

# 	query = f"""
# 	SELECT 
# 		CASE WHEN rn = 1 THEN t.name ELSE '' END AS name,
# 		CASE WHEN rn = 1 THEN t.property_name ELSE '' END AS property_name,
# 		CASE WHEN rn = 1 THEN t.contract_start_date ELSE NULL END AS period_start_date,
# 		CASE WHEN rn = 1 THEN t.status ELSE '' END AS status,
# 		CASE WHEN rn = 1 THEN t.yearly_rent ELSE '' END AS rental_amount,
# 		CASE WHEN rn = 1 THEN t.admin_fee ELSE '' END AS admin_fee,
# 		CASE WHEN rn = 1 THEN t.sec_dep_cash ELSE '' END AS sec_dep_cash,
# 		CASE WHEN rn = 1 THEN t.sec_dep_chq ELSE '' END AS sec_dep_chq,
# 		CASE WHEN rn = 1 THEN t.vat ELSE '' END AS vat,
# 		CASE WHEN rn = 1 THEN t.total_amount ELSE '' END AS total_amount,
# 		CASE WHEN rn = 1 THEN t.installment ELSE '' END AS installment,
# 		CASE WHEN rn = 1 THEN t.contract_end_date ELSE NULL END AS period_end_date,
# 		t.payment_amount AS payment_amount,
# 		CASE 
# 			WHEN rn = 1 AND t.outstanding_amount != 0 
# 			THEN ROUND(t.outstanding_amount, 2) 
# 			ELSE NULL 
# 		END AS outstanding_amount,
# 		t.payment_scheduled_date
# 	FROM (
# 		SELECT 
# 			tc.name,
# 			tc.property_name,
# 			tc.contract_start_date,
# 			tc.contract_end_date,
# 			ROUND(tc.yearly_rent, 2) AS yearly_rent,
# 			ps.payment_scheduled_date,
# 			ROUND(ps.payment_amount, 2) AS payment_amount,
# 			ut.status,
# 			ROUND(toc.admin_fee, 2) AS admin_fee,
# 			ROUND(toc.sec_dep_cash, 2) AS sec_dep_cash,
# 			ROUND(toc.sec_dep_chq, 2) AS sec_dep_chq,
# 			ROUND(tc.yearly_rent * 0.05, 2) AS vat,
# 			ROUND(tc.yearly_rent + IFNULL(toc.admin_fee,0) + tc.yearly_rent * 0.05, 2) AS total_amount,
# 			ROW_NUMBER() OVER (PARTITION BY tc.name ORDER BY ps.payment_scheduled_date) AS rn,
# 			COUNT(ps.name) OVER (PARTITION BY tc.name) AS installment,
# 			IFNULL(si.outstanding_amount, 0) AS outstanding_amount
# 		FROM 
# 			`tabTenancy Contract` AS tc
# 		LEFT JOIN 
# 			`tabTC Payment Schedule` AS ps  
# 			ON ps.parent = tc.name
# 		LEFT JOIN
# 			`tabUnit` AS ut 
# 			ON ut.name = tc.unit_number
# 		LEFT JOIN (
# 			SELECT custom_tenancy_contract, ROUND(MAX(outstanding_amount), 2) AS outstanding_amount
# 			FROM `tabSales Invoice`
# 			where docstatus = 1
# 			GROUP BY custom_tenancy_contract
# 		) AS si 
# 			ON si.custom_tenancy_contract = tc.name
# 		LEFT JOIN (
# 			SELECT 
# 				parent,
# 				MAX(CASE WHEN particulars = 'Admin Fee' THEN ROUND(amount, 2) END) AS admin_fee,
# 				MAX(CASE WHEN particulars = 'Security Deposit (Refundable)' AND is_pdc = 0 THEN ROUND(amount, 2) END) AS sec_dep_cash,
# 				MAX(CASE WHEN particulars = 'Security Deposit (Refundable)' AND is_pdc = 1 THEN ROUND(amount, 2) END) AS sec_dep_chq
# 			FROM `tabType Of Charges`
# 			GROUP BY parent
# 		) AS toc
# 			ON toc.parent = tc.name
# 		{where_clause}
# 	) t
# """

	query = f"""
	SELECT 
		CASE WHEN rn = 1 THEN t.name ELSE '' END AS name,
		CASE WHEN rn = 1 THEN t.property_name ELSE '' END AS property_name,
		CASE WHEN rn = 1 THEN t.contract_start_date ELSE NULL END AS period_start_date,
		CASE WHEN rn = 1 THEN t.status ELSE '' END AS status,
		CASE WHEN rn = 1 THEN t.yearly_rent ELSE '' END AS rental_amount,
		CASE WHEN rn = 1 THEN t.admin_fee ELSE '' END AS admin_fee,
		CASE WHEN rn = 1 THEN t.sec_dep_cash ELSE '' END AS sec_dep_cash,
		CASE WHEN rn = 1 THEN t.sec_dep_chq ELSE '' END AS sec_dep_chq,
		CASE WHEN rn = 1 THEN t.vat ELSE '' END AS vat,
		CASE WHEN rn = 1 THEN t.total_amount ELSE '' END AS total_amount,
		CASE WHEN rn = 1 THEN t.installment ELSE '' END AS installment,
		CASE WHEN rn = 1 THEN t.contract_end_date ELSE NULL END AS period_end_date,
		t.payment_amount AS payment_amount,
		CASE 
			WHEN rn = 1 AND t.outstanding_amount != 0 
			THEN ROUND(t.outstanding_amount, 2) 
			ELSE NULL 
		END AS outstanding_amount,
		t.payment_scheduled_date,
		CASE WHEN rn = 1 THEN t.allocated_amount ELSE NULL END AS paid_amount
	FROM (
		SELECT 
			tc.name,
			tc.property_name,
			tc.contract_start_date,
			tc.contract_end_date,
			ROUND(tc.yearly_rent, 2) AS yearly_rent,
			ps.payment_scheduled_date,
			ROUND(ps.payment_amount, 2) AS payment_amount,
			ut.status,
			ROUND(toc.admin_fee, 2) AS admin_fee,
			ROUND(toc.sec_dep_cash, 2) AS sec_dep_cash,
			ROUND(toc.sec_dep_chq, 2) AS sec_dep_chq,
			ROUND(tc.total_taxes_and_charges ) AS vat,
			ROUND(tc.grand_total) AS total_amount,
			ROW_NUMBER() OVER (PARTITION BY tc.name ORDER BY ps.payment_scheduled_date) AS rn,
			COUNT(ps.name) OVER (PARTITION BY tc.name) AS installment,
			IFNULL(si.outstanding_amount, 0) AS outstanding_amount,
			si.allocated_amount 
		FROM 
			`tabTenancy Contract` AS tc
		LEFT JOIN 
			`tabTC Payment Schedule` AS ps  
			ON ps.parent = tc.name
		LEFT JOIN
			`tabUnit` AS ut 
			ON ut.name = tc.unit_number
		LEFT JOIN (
			SELECT si.custom_tenancy_contract, ROUND(MAX(si.outstanding_amount), 2) AS outstanding_amount, sum(py.allocated_amount)  as allocated_amount
			FROM `tabSales Invoice` as si
			left join `tabPayment Entry Reference` as py on py.reference_name = si.name 
			where si.docstatus = 1 and py.docstatus =1
			GROUP BY custom_tenancy_contract, si.name
		) AS si 
			ON si.custom_tenancy_contract = tc.name
		LEFT JOIN (
			SELECT 
				parent,
				MAX(CASE WHEN particulars = 'Admin Fee' THEN ROUND(amount, 2) END) AS admin_fee,
				MAX(CASE WHEN particulars = 'Security Deposit (Refundable)' AND is_pdc = 0 THEN ROUND(amount, 2) END) AS sec_dep_cash,
				MAX(CASE WHEN particulars = 'Security Deposit (Refundable)' AND is_pdc = 1 THEN ROUND(amount, 2) END) AS sec_dep_chq
			FROM `tabType Of Charges`
			GROUP BY parent
		) AS toc
			ON toc.parent = tc.name
		{where_clause}
	) t
	
	"""

	return frappe.db.sql(query, params, as_dict=True)
