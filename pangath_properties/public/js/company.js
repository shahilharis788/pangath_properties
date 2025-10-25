frappe.ui.form.on('Company', {
	refresh(frm) {
		frm.set_query("default_rental_income", function() {
            return {
            "filters": {
            "is_group": 0,
            "company": frm.doc.name
            }
            };
            });
	}
})