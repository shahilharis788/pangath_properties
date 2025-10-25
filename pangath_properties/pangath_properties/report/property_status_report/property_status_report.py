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
			pty.name as name,
			pty.id as id,
			pty.property_no as property_no,
			pty.status as status,
			pty.property_type as property_type,
			pty.property_owner as property_owner,
			pty.no_of_floors as no_of_floors,
			pty.no_of_units as no_of_units,
			pty.tower_type as tower_type,
			pty.builtup_area as builtup_area,
			pty.plot_area as plot_area,
			pty.default_rent_per_unit as default_rent_per_unit,
			pty.default_rent_per_unit * pty.no_of_units as expected_rent
		FROM
			`tabProperty` AS pty 
	"""
    if filters.property:
        query = f"{query} WHERE pty.name = '{filters.property}'"

    data = frappe.db.sql(f"{query}", as_dict=True)
    return data

def get_columns(filters):
    columns = [
        {
            'fieldname': 'name',
            'label': _('Name'),
            'fieldtype': 'Link',
            'options': 'Property',
            'width': 'auto'
        },
        {
            'fieldname': 'id',
            'label': _('ID'),
            'fieldtype': 'Data',
            'width':'auto'
        },
        {
            'fieldname': 'property_no',
            'label': _('Title Deed No'),
            'fieldtype': 'Data',
            'width': 'auto',
			"align": "left"

        },
        {
            'fieldname': 'status',
            'label': _('Status'),
            'fieldtype': 'Data',
            'width': 'auto',
			"align": "left"
        },
        {
            'fieldname': 'property_type',
            'label': _('Property Type'),
            'fieldtype': 'Data',
            'width': 'auto'
        },
   		{
            'fieldname': 'property_owner',
            'label': _('Property Owner'),
            'fieldtype': 'Link',
			'options': 'Property Owner',
            'width': 'auto',
			"align": "left"
        },
		{
            'fieldname': 'no_of_floors',
            'label': _('No Of Floors'),
            'fieldtype': 'Data',
            'width': 'auto',
			"align": "left"
        },
		{
            'fieldname': 'tower_type',
            'label': _('Tower Type'),
            'fieldtype': 'Data',
            'width': 'auto',
			"align": "left"

        },
		{
            'fieldname': 'builtup_area',
            'label': _('Builtup Area'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
		{
            'fieldname': 'plot_area',
            'label': _('Plot Area'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
		{
            'fieldname': 'default_rent_per_unit',
            'label': _('Default Rent Per Unit'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
		{
            'fieldname': 'expected_rent',
            'label': _('Expected Rent'),
            'fieldtype': 'Float',
            'width': 'auto'
        },
    ]
    return columns