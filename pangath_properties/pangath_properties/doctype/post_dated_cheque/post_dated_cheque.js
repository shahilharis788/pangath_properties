// Copyright (c) 2024, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Post Dated Cheque", {
    refresh(frm) {
        frm.set_query('party_type', function (doc) {
            return {
                filters: {
                    "name": ["in", ["Customer", "Employee", "Shareholder", "Supplier"]]
                }
            };
        });
        if(frm.doc.docstatus ==1){
            frm.add_custom_button(__('Received'),function () {
               
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Received"
                    },
                });
               
            }, __('Cheque Status'));
            frm.add_custom_button(__('Cancelled'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Cancelled"
                    },
                    
                });
            }, __('Cheque Status'));
            frm.add_custom_button(__('Bounced'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Bounced"
                    },
                    
                });
            }, __('Cheque Status'));
            frm.add_custom_button(__('Returned'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Returned"
                    },
                    
                });
            }, __('Cheque Status'));
            frm.add_custom_button(__('Rejected'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Rejected"
                    },
                    
                });
            }, __('Cheque Status'));
            frm.add_custom_button(__('Expired'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Expired"
                    },
                    
                });
            }, __('Cheque Status'));
            frm.add_custom_button(__('Cleared'),function () {
                frappe.call({
                    'method': 'pangath_properties.pangath_properties.doctype.post_dated_cheque.post_dated_cheque.cheque_status',
                    'args': {
                        "name": frm.doc.name,
                        "status":"Cleared"
                    },
                    
                });
            }, __('Cheque Status'));
        }
      
    },
    onload(frm) {    
        account_fileter(frm);
    }
});


var account_fileter = (frm) =>{
frm.set_query("bank_account", function() {
  return {
    filters: {
      account_type: "Bank",
        company: frm.doc.company
    }
  };
});
}