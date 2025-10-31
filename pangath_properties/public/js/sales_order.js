frappe.ui.form.on("Sales Order",{
    refresh: function(frm){
        setTimeout(() => {
			frm.set_query('unit', function (doc) {
				let filters = []
				return {
					"filters": filters
				};
			})
		}, 1000);
        frm.add_custom_button(__('Proforma Invoice'), function() {
            frappe.model.open_mapped_doc({
                method: "pangath_properties.events.sales_order.make_proforma_invoice",
                frm: frm
            });
        }, __('Create'));
    
    }
})