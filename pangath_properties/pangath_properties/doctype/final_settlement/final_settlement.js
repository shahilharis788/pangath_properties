// Copyright (c) 2024, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Final Settlement", {
	refresh(frm) {
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__("Payment Entry"), () => {
                frappe.model.open_mapped_doc({
                    method: "real_estate.real_estate.doctype.final_settlement.final_settlement.create_payment_entry",
                    frm:frm
                })
                
            });
        }
	},
});

