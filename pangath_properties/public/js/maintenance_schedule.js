


frappe.ui.form.on("Maintenance Schedule", {
    refresh: function(frm) {
        if(frm.doc.docstatus ==1){
            frm.add_custom_button(__('Material Request'),function () {
                frappe.model.open_mapped_doc({
                    method: "real_estate.events.maintenance_schedule.create_material_request",
                    frm:frm
                })
            },__('Create'));
        }
    },
    
   custom_tenancy_contract: function(frm) {
        if (frm.doc.custom_tenancy_contract) {
            frappe.db.get_value("Tenancy Contract", frm.doc.custom_tenancy_contract, ["customer_name", "property_name"])
                .then(r => {
                    if (r.message) {
                        frm.set_value("customer", r.message.customer_name);
                        frm.set_value("custom_property", r.message.property_name);  
                    }
                 });
        }
        if((frm.doc.custom_tenancy_contract == "") && (frm.doc.customer)){
                frm.set_value("customer", "");
        }
        if((frm.doc.custom_tenancy_contract == "") && (frm.doc.custom_property)){
             frm.set_value("custom_property", ""); 
        }
    }
    
});