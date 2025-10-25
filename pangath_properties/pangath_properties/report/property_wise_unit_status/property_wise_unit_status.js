// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Property Wise Unit Status"] = {
	"filters": [
		{
			'fieldname':'property',
			'label':__('Property'),
			'fieldtype':'Link',
			'options': 'Property',
			'width':100,
		}
	]
};
