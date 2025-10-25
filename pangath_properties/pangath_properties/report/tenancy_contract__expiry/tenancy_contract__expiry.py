# Copyright (c) 2023, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_data(filters):
    query = f"""
	SELECT 
    	COUNT(tc.name) AS name,
		tc.name AS tenancy_contract,
        tc.unit_number as unit,
        tc.yearly_rent as rent,
        ps.payment_frequency as payment_frequency,
        ps.period_start_date as start_date,
        ps.period_end_date as end_date,
        st.sales_person as sales_person,
        c.customer_name as customer,
        tc.remarks
	FROM 
    	`tabTenancy Contract` tc
	LEFT JOIN 
    	`tabTA Payment Schedule` ps ON ps.parent = tc.name
    LEFT JOIN
        `tabSales Team` st ON st.parent = tc.name
    LEFT JOIN
        `tabCustomer` c ON c.name = tc.name_of_tenant
	WHERE
        ps.period_end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 MONTH) AND tc.docstatus =1
	GROUP BY
    	tc.name;
	"""
    data = frappe.db.sql(f"{query}", as_dict=True)
    return data

def get_columns(filters):
    columns = [
		{
            'fieldname': 'tenancy_contract',
            'label': _('Tenancy Contract'),
            'fieldtype': 'Link',
            'options': 'Tenancy Contract',
            'width': 'auto'
        },
        {
            'fieldname': 'customer',
            'label': _('Customer'),
            'fieldtype': 'Data',
            'width': 'auto'
        },
        {
            'fieldname': 'unit',
            'label': _('Unit'),
            'fieldtype': 'Link',
            'options': 'Unit',
            'width': 'auto'
        },
        {
            'fieldname': 'rent',
            'label': _('Rent Amount'),
            'fieldtype': 'currency',
            'width': 'auto'
        },
        {
            'fieldname': 'payment_frequency',
            'label': _('Payment Frequency'),
            'fieldtype': 'data',
            'width': 'auto'
        },
        {
            'fieldname': 'start_date',
            'label': _('Start Date'),
            'fieldtype': 'date',
            'width': 'auto'
        },
        {
            'fieldname': 'end_date',
            'label': _('End Date'),
            'fieldtype': 'date',
            'width': 'auto'
        },
        {
            'fieldname': 'sales_person',
            'label': _('Sales Person'),
            'fieldtype': 'Link',
            'options':'Sales Person',
            'width': 'auto'
        },
        {
            'fieldname': 'remarks',
            'label': _('Remarks'),
            'fieldtype': 'Data',
            'width': 'auto'
        },
    ]
    return columns