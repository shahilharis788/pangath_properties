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
			ta.name as name,
			ta.tenant_name as tenant_name,
			ta.type as tenant_type,
			ta.email as email,
			ta.gender as gender,
			ta.territory as territory,
			ta.property_name as property_name,
			ta.unit as unit,
			ta.parking_required as parking,
			ta.yearly_rent as yearly_rent,
			ta. monthly_rent  as monthly_rent
		FROM
			`tabTenancy Application` AS ta
		WHERE
			ta.workflow_state = 'Approved'
	"""
    if filters.customer:
        query = f"{query} AND ta.tenant_name = '{filters.customer}'"
    data = frappe.db.sql(f"{query}", as_dict=True)
    return data

def get_columns(filters):
    columns = [
        {
            'fieldname': 'name',
            'label': _('Name'),
            'fieldtype': 'Link',
            'options': 'Tenancy Application',
            'width': 150
        },
		{
            'fieldname': 'tenant_name',
            'label': _('Tenant Name'),
            'fieldtype': 'Link',
            'options': 'Customer',
            'width': 150
        },
        {
            'fieldname': 'tenant_type',
            'label': _('Tenant Type '),
            'fieldtype': 'Data',
            'width': 125
        },
        {
            'fieldname': 'email',
            'label': _('Email '),
            'fieldtype': 'Data',
            'width': 'auto'
        },
        {
            'fieldname': 'gender',
            'label': _('Gender'),
            'fieldtype': 'Data',
            'width': 'auto',
			"align": "left"
        },
        {
            'fieldname': 'territory',
            'label': _('Territory'),
            'fieldtype': 'Data',
            'width': 'auto'
        },
        {
            'fieldname': 'property_name',
            'label': _('Property Name '),
            'fieldtype': 'Link',
			'options': 'Property',
            'width': 'auto',
			"align": "left"
        },
   		{
            'fieldname': 'unit',
            'label': _('Unit'),
            'fieldtype': 'Link',
			'options': 'Unit',
            'width': 'auto',
			"align": "left"
        },
		{
            'fieldname': 'parking',
            'label': _('Parking'),
            'fieldtype': 'Link',
			'options': 'Unit',
            'width': 'auto',
			"align": "left"
        },
		{
            'fieldname': 'yearly_rent',
            'label': _('Yearly Rent'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
		{
            'fieldname': 'monthly_rent',
            'label': _('Monthly Rent'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
    ]
    return columns