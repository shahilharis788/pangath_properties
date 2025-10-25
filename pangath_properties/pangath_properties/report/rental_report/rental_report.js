// Copyright (c) 2025, iterative and contributors
// For license information, please see license.txt

frappe.query_reports["Rental Report"] = {
	"filters": [
		{
			fieldname: "contract_name",
			label: __("Contract Name"),
			fieldtype: "Link",
			options: "Tenancy Contract",
			reqd: 0
		},
		{
			fieldname: "property_name",
			label: __("Property Name"),
			fieldtype: "Link",
			options: "Property",
			reqd: 0
		}
	]
};
