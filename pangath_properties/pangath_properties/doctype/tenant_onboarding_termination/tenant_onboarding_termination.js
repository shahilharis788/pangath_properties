// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenant Onboarding Termination', {
	// refresh: function(frm) {

	// }
	refresh:function(frm){
		frm.fields_dict.rental_income.$wrapper.find('.grid-add-row').remove()
		frm.fields_dict.reverse_deferred_revenue.$wrapper.find('.grid-add-row').remove()
		if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Payment Entry'), () => {
				return frappe.call({
					method: 'pangath_properties.pangath_properties.doctype.tenant_onboarding_termination.tenant_onboarding_termination.create_payment_entry',
					args: { 'doc': frm.doc },
					callback: function(r) {
						frappe.set_route("Form", "Payment Entry", r.message);
					}
				});
			}, __('Create'));

			}
			}
});
frappe.ui.form.on("Penality And Other Expenses",{
	particulars:function(frm,cdt,cdn){
		let row=locals[cdt][cdn]
		frappe.db.get_doc("Particulars",row.particulars)
			.then((doc) => {
				if(doc.accounts.length && doc.accounts.length > 0){
					doc.accounts.forEach(i => {
							if(i.company == frm.doc.company){
								if(i.default_account){
									frappe.model.set_value(row.doctype,row.name,'account',i.default_account)
							}
						}
					});
				}
				else{
					frappe.model.set_value(row.doctype,row.name,'account','')
				}
			});
	}
})