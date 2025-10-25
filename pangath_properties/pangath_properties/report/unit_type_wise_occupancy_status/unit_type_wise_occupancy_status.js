// Copyright (c) 2024, iterative and contributors
// For license information, please see license.txt

frappe.query_reports["Unit type Wise Occupancy Status"] = {
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
