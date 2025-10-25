// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Unit Status Report"] = {
	"filters": [
		{
			'fieldname':'company',
			'label':__('Company'),
			'fieldtype':'Link',
			'options': 'Company',
			'width':100,
		},
		{
			'fieldname':'status',
			'label': __("Status"),
			'fieldtype':'MultiSelectList',
			'options': "\nLeased\nBooked\nAvailable\nSold\nNot Hand Over".split('\n').filter(Boolean),
			'width':100,
			'default': "\nLeased\nBooked\nAvailable\nSold\nNot Hand Over".split('\n').filter(Boolean)
		},
		{
			'fieldname':'property',
			'label':__('Property Name'),
			'fieldtype':'Link',
			'options': 'Property',
			'width':100,
		},
		{
			'fieldname':'unit_name',
			'label':__('Unit Name'),
			'fieldtype':'Data',
			'width':100,
		},
		{
			'fieldname':'unit_type',
			'label':__('Unit Type'),
			'fieldtype':'Link',
			'options': 'Unit Type',
			'width':100,
		},
		
	],
	formatter: function(value, row, column, data, default_formatter) {
		var color = "";
		switch(value) {
			case 'Leased':
				color = 'blue';
				break;
			case 'Booked':
				color = 'red';
				break;
			case 'Available':
				color = 'green';
				break;
			case 'Sold':
				color = 'orange';
				break;
			case 'Not Hand Over':
				color = 'purple';
				break;
			default:
				color = 'black';
		}
		return `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
	}
};
