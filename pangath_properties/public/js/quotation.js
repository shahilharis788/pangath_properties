// frappe.ui.form.on('Quotation', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Tenancy Application'), function() {
//             frappe.model.open_mapped_doc({
// 				method: "real_estate.events.quotation.create_tenancy_application",
// 				frm:frm
// 			})
//         }, __('Create'));  // Group under 'Actions' menu (optional)
//     }
// });


frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        frm.add_custom_button(__('Tenancy Contract'), function () {
            frm.doc.items.forEach(function(item) {
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Unit",
                        filters: {
                            name: item.item_code 
                        },
                        fieldname: "property"
                    },
                    callback: function(r) {
                        frappe.new_doc('Tenancy Contract', {
                            name_of_tenant: frm.doc.customer_name,
                            quotation: frm.doc.name,
                            contact_person: frm.doc.contact_person,
                            contact_email: frm.doc.contact_email,
                            contact_mobile: frm.doc.contact_mobile,
                            unit_number: item.item_code,
                            property_name: r.message ? r.message.property : "",
                            unit_type: item.uom
                        });
                    }
                });
            });
        }, __('Create'));
    }
});