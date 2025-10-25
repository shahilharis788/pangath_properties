// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Tenant Information Form"] = {
	"filters":
		[
			{
				fieldname: "customer",
				label: __("Customer "),
				fieldtype: "Link",
				options: "Customer"
			}
		],
}