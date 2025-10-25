// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unit', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on("Charges",{
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
