// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt


frappe.ui.form.on('Particulars', {
	refresh(frm) {
		frm.set_query("default_account", "accounts", function (doc, cdt, cdn) {
			let row = locals[cdt][cdn]
			return {
				filters: {
					company: row.company
				}
			};
		})
	}
})