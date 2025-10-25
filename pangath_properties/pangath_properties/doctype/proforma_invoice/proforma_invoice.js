// Copyright (c) 2025, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Proforma Invoice", {
    refresh(frm) {
        if (cur_frm.doc.docstatus == 1){
        frm.add_custom_button(__('Sales Invoice'), function() {
            frappe.model.open_mapped_doc({
                method: "real_estate.real_estate.doctype.proforma_invoice.proforma_invoice.make_sales_invoice_from_proforma",
                frm: frm
            });
        }, __('Create'));
        }
    }
});