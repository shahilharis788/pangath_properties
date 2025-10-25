// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Outstanding PDC Report"] = {
	"filters": [
		{
			'fieldname':'customer',
			'label':__('Customer'),
			'fieldtype':'Link',
			'options': 'Customer',
			'width':100,
		},
		{
			'fieldname':'from_date',
			'label':__('From Date'),
			'fieldtype':'Date',
			'width':100,
		},
		{
			'fieldname':'to_date',
			'label':__('To Date'),
			'fieldtype':'Date',
			'width':100,
		},
		{
			'fieldname':'tenant_onboarding',
			'label':__('Tenant Onboarding'),
			'fieldtype':'Link',
			'options': 'Tenant Onboarding',
			'width':100,
		},
	]
};
