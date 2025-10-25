// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenancy Agreement', {
	onload: function (frm) {
		frm.set_query('unit', function (doc) {
			return {
				"filters": [
					["Unit", "property", "=", frm.doc.property]
				]
			};
		})
}
});
