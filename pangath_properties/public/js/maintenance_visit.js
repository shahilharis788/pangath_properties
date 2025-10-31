frappe.ui.form.on("Maintenance Visit",{
    
    
    refresh:function(frm){
        if(frm.doc.maintenance_schedule){
            frm.set_df_property('customer', 'read_only', 1);
            frm.set_df_property('custom_tenancy_contract', 'read_only', 1);
            frm.set_df_property('custom_property', 'read_only', 1);
        }
        
        if(frm.doc.docstatus == 1){
        frm.add_custom_button(__("Material Request"), function(){
			frappe.call({
				method: 'pangath_properties.events.maintenance_visit.create_material_request',
				args: { 'doc': frm.doc.name},
				callback: function(r) {
					if (r && r.message) {pangath_properties
						var doc = frappe.model.sync(r.message);
					frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
				
			});
		  },);
        }
        if(frm.doc.docstatus == 1){
          frm.add_custom_button(__("Sales Invoice"), function(){
			frappe.call({
				method: 'pangath_properties.events.maintenance_visit.create_sales_invoice',
				args: { 'doc': frm.doc.name },
				callback: function(r) {
					if (r && r.message) {
						var doc = frappe.model.sync(r.message);
					frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
				
			});
		  },);
        }  
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__("Material Issue"), function(){
              frappe.call({
                  method: 'pangath_properties.events.maintenance_visit.create_material_issue',
                  args: { 'doc': frm.doc.name },
                  callback: function(r) {
                      if (r && r.message) {
                          var doc = frappe.model.sync(r.message);
                      frappe.set_route("Form", r.message.doctype, r.message.name);
                      }
                  }
                  
              });
            },);
        }
        if(frm.doc.maintenance_schedule && frm.doc.__islocal && frm.doc.issue){
            frappe.db.get_value("Maintenance Schedule",frm.doc.maintenance_schedule,"issue").then(r => {
                frappe.db.get_doc("Issue",r.message.issue).then( res =>{
                    frm.set_value("customer",res.customer)
                    frm.set_value("custom_tenancy_contract",res.custom_tenancy_contract)
                    frm.set_value("custom_property",res.property)
                    frm.set_value("custom_unit_no",res.unit)

                })
            })
        } 
    },
    
})
