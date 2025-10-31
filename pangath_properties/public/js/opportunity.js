frappe.ui.form.on("Opportunity", {
	refresh: function (frm) {
		frm.add_custom_button(__("Site Visit Schedule"), () => {
			frappe.model.open_mapped_doc({
				method: "pangath_properties.events.opportunity.schedule_site_visit",
				frm:frm
			})
			
		}, ("Create"));
		frm.add_custom_button(__("Tenancy Application"), () => {
			frappe.model.open_mapped_doc({
				method: "pangath_properties.events.opportunity.create_tenancy_application",
				frm:frm
			})
			
		}, ("Create"));
	},
	onload:function(frm){
		let prev_route = frappe.get_prev_route();
		let prev_doctype = prev_route[1];
		let prev_docname = prev_route[2];

		if ((prev_doctype === "Lead") && prev_docname) {
			
    		frappe.db.get_value("Lead", prev_docname, ["custom_property", "custom_unit"]).then(r => {
        		if (r && r.message) {
            		let property = r.message.custom_property;
            		let unit = r.message.custom_unit;
					let ut = "";
            		let utn = "";

           
            	frappe.db.get_value("Unit", unit, ["unit_type", "unit_no"])
                	.then(res => {
                    	if (res && res.message) {
                        	ut = res.message.unit_type || "";
                        	utn = res.message.unit_no || "";
                    	}

                    
                    	let child = frm.add_child("custom_property_and_unit", {
                        	property: property,
                        	unit: unit,
                        	unit_type: ut,
                        	unit_no: utn
                    	});

                    	frm.refresh_field("custom_property_and_unit");
                	})
                	.catch(() => {
                    	let child = frm.add_child("custom_property_and_unit", {
                        	property: property,
                        	unit: unit,
                        	unit_type: "",
                        	unit_no: ""
                    	});
						frm.refresh_field("custom_property_and_unit");
                	});
        		}
    		});

		}
		if(!frm.doc.__islocal){
			if (window.history && window.history.pushState){
				window.history.pushState('forward', null, '');
			$(window).on('popstate', function() {
				location.reload();
			});
			}
		}
	}
});

frappe.ui.form.on("Opportunity Item", {
	item_code: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if (row.item_code) {
			frappe.db.get_value("Unit", row.item_code, "rent")
			.then(r => {
				if (r.message.rent) {
					frappe.model.set_value(cdt, cdn, "rate", r.message.rent)
				} else {
					frappe.model.set_value(cdt, cdn, "rate", 0)
				}
			})
		}
	}
});

frappe.ui.form.on("Property And Unit", {
	unit: function (frm, cdt, cdn) {
		let child = locals[cdt][cdn];
		let exists = false;
		// Iterate through the child table to check if the unit already exists
		frm.doc.custom_property_and_unit.forEach(function (row) {
			if (row.unit === child.unit && row.name !== child.name) {
				exists = true;
			}
		});
		// frappe.db.get_value("Unit",child.unit,["rent","monthly_rent"]).then(r =>{

			// frappe.model.set_value(cdt,cdn,"yearly_rent",r.message.rent)
			// frappe.model.set_value(cdt,cdn,"monthly_rent",r.message.monthly_rent)

		// })
		frappe.db.get_doc("Unit",child.unit).then(r =>{
			r.payment_frequency.forEach(function(pay){
				if(pay.payment_frequency == child.payment_frequency) {
					frappe.model.set_value(cdt,cdn,"yearly_rent",pay.amount)
					frappe.model.set_value(cdt,cdn,"monthly_rent",pay.amount/12)
				}
			})
		})
		// Throw a message if the unit already exists in the child table
		if (exists) {
			frappe.throw(__("The selected unit is already in the list."));
		}
	},
	yearly_rent:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
		frappe.model.set_value(cdt,cdn,"monthly_rent",child.yearly_rent/12)
	},
	payment_frequency:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
		frappe.db.get_doc("Unit",child.unit).then(r =>{
			r.payment_frequency.forEach(function(pay){
				if(pay.payment_frequency == child.payment_frequency) {
					frappe.model.set_value(cdt,cdn,"yearly_rent",pay.amount)
					frappe.model.set_value(cdt,cdn,"monthly_rent",pay.amount/12)
				}
			})
		})
	}

});
