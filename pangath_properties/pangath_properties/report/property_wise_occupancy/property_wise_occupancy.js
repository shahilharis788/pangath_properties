// Copyright (c) 2022, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Property Wise Occupancy"] = {
	"filters": [
		{
			'fieldname':'property',
			'label':__('Property'),
			'fieldtype':'Link',
			'options': 'Property',
			'width':100,
		},
		{
			'fieldname':'unit',
			'label':__('Unit'),
			'fieldtype':'Link',
			'options': 'Unit',
			'width':100,
		},

	]
};
