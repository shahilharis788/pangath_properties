frappe.ui.form.on("Issue", {
	onload: function (frm) {
		frm.set_query('unit', function (doc) {
			let filters = []
			if (frm.doc.property) {
				filters.push(["Unit", "property", "in", frm.doc.property])
			}
			return {
				"filters": filters
			};
		})
	},
	refresh: function(frm) {
		// hide + icon of  Task from connection 
		setTimeout(() => {
			$("[data-doctype='Task']").find("button").hide();
		  }, 10);
		  frm.add_custom_button(__("Create Maintenance Schedule"), function(){
			frappe.call({
				method: 'real_estate.events.issue.create_maintenance_schedule',
				args: { 'doc': frm.doc.name },
				callback: function(r) {
					if (r && r.message) {
						var doc = frappe.model.sync(r.message);
					frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
			});
		  },);
	},
	unit:function(frm){
		frappe.db.get_value("Tenancy Contract",filters = {"property_name":frm.doc.property,"unit_number":frm.doc.unit},["name","name_of_tenant"]).then(r =>{
			frm.set_value("custom_tenancy_contract",r.message.name)
			frm.set_value("customer",r.message.name_of_tenant)

		})
	},
	custom_tenancy_contract:function(frm){
		frappe.db.get_value("Tenancy Contract",frm.doc.custom_tenancy_contract,["property_name","unit_number","name_of_tenant"]).then(r =>{
			frm.set_value("property",r.message.property_name)
			frm.set_value("customer",r.message.name_of_tenant)
			frm.set_value("unit",r.message.unit_number)
		})
	}
});