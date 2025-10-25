// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Property Status Report"] = {
	"filters":
		[
			{
				fieldname: "property",
				label: __("Property"),
				fieldtype: "Link",
				options: "Property"
			}
		],
};
