// Copyright (c) 2025, iterative and contributors
// For license information, please see license.txt


frappe.ui.form.on('Tenancy Application', {
    before_save:function(frm){
		 frm.set_df_property('naming_series', 'hidden', 1);
	},
    yearly_rent(frm){
        frm.set_value("total", frm.doc.yearly_rent + frm.doc.total_charges)
    },
    total_charges(frm){
        frm.set_value("total", frm.doc.yearly_rent + frm.doc.total_charges)
    },
    customer:function(frm){
            if(frm.doc.customer){
				frm.set_value("tenant_name", frm.doc.customer)
                frappe.db.get_value("Customer", frm.doc.customer, ["custom_emirate_id", "tax_id", "payment_terms", "custom_passport_no", "custom_nationality", "custom_contact_no", "customer_name"]).then(r=>{
                    if(r.message){
                        frm.set_value("custom_emirates_id", r.message.custom_emirate_id)
						frm.set_value("contact_no", r.message.custom_contact_no)
						frm.set_value("nationality", r.message.custom_nationality)
						frm.set_value("tax_id", r.message.tax_id)
						frm.set_value("payment_terms_template",  r.message.payment_terms)
						frm.set_value("passport_no",  r.message.custom_passport_no)
						frm.set_value("customer_name",  r.message.customer_name)

                    }
                })
                frappe.db.get_value("Customer", frm.doc.customer, "customer_primary_address").then(r=>{
                    if(r.message){
                        
                        frappe.db.get_value("Address", r.message.customer_primary_address, "email_id").then(r=>{
                            if(r.message){
                               
                                frm.set_value("email", r.message.email_id)
                            }
                        })
                    }
                })
            }
        
    },
	
    refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Booking Agreement'),function () {
                frappe.model.open_mapped_doc({
                    method: "pangath_properties.pangath_properties.doctype.tenancy_application.tenancy_application.create_booking_agreement",
                    frm:frm,
                    args:{

                    }
                })
			},__('Create'));
            frm.add_custom_button(__('Tenancy Contract'),function () {
                frappe.model.open_mapped_doc({
                    method: "pangath_properties.pangath_properties.doctype.tenancy_application.tenancy_application.create_tenancy_contract",
                    frm:frm
                })
			},__('Create'));
            // frm.add_custom_button(__('Payment Entry'),function () {
            //     frappe.model.open_mapped_doc({
            //         method: "pangath_properties.pangath_properties.doctype.tenancy_application.tenancy_application.create_payment_entry",
            //         frm:frm
            //     })
			// },__('Create'));
            
		}
		if (frm.doc.opportunity && frm.doc.__islocal && !frm.doc.property_name) {
        let d = new frappe.ui.Dialog({
            title: 'Select Property And Unit',
            fields: [
                {
                    fieldname: 'property_units',
                    fieldtype: 'Table',
                    label: 'Property Units',
                    fields: [
                        {
                            fieldname: 'property',
                            fieldtype: 'Data',
                            label: 'Property',
                            in_list_view: 1
                        },
                        {
                            fieldname: 'unit',
                            fieldtype: 'Data',
                            label: 'Unit',
                            in_list_view: 1
                        },
                        {
                            fieldname: 'unit_no',
                            fieldtype: 'Data',
                            label: 'Unit No',
                            in_list_view: 1
                        },
                        {
                          fieldname: 'unit_type',
                          fieldtype: 'Data',
                          label: 'Unit Type',
                          in_list_view: 1
                        },
                        {
                          fieldname: 'yearly_rent',
                          fieldtype: 'Data',
                          label: 'Yearly Rent',
                          in_list_view: 1
                        },
                    ]
                }
            ],
            size: 'large', // small, large, extra-large 
            primary_action_label: 'Submit',
            primary_action(values) {
              if (values.property_units && values.property_units.length > 0){
                let selected_data  = d.fields_dict.property_units.grid.get_selected_children();
              if (selected_data.length == 1) {
                let details = selected_data.map(item => ({
                  property: item.property,
                  unit: item.unit,
                  unit_type:item.unit_type,
                  yearly_rent:item.yearly_rent
              }));
              console.log(details)
              if (details.length > 0) {
                  let first_item = details[0];
                  frm.set_value('property_name', first_item.property);
                  frm.set_value('unit', first_item.unit);
                  frm.set_value('unit_type', first_item.unit_type);
                  frm.set_value("yearly_rent",first_item.yearly_rent);
                  frm.set_value("monthly_rent",first_item.yearly_rent/12)
              }
              }
              if(selected_data.length >1){
                  frappe.throw("Select Only One Row")
              }
            }
                d.hide();
            }
        });
    
        frappe.db.get_doc('Opportunity', frm.doc.opportunity).then(r => {
            if (r) {
                const property_units_data = r.custom_property_and_unit || [];
    
                // Clear existing rows and add new rows to the table
                d.fields_dict.property_units.grid.df.data = [];
                property_units_data.forEach(row => {
                    d.fields_dict.property_units.grid.df.data.push({
                        property: row.property,
                        unit: row.unit,
                        unit_no: row.unit_no,
                        unit_type:row.unit_type,
                        yearly_rent:row.yearly_rent
                    });
                });
    
                // Refresh the table grid
                d.fields_dict.property_units.grid.refresh();
            }
        }).catch(err => {
            console.error('Error fetching Opportunity:', err);
        });
    
        d.show();
    }

	},
	onload: function (frm) {
        frm.fields_dict["unit_details"].grid.get_field("unit").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "status": ["!=", "Rented"],
                    "property": locals[cdt][cdn].property
                }
            };
        };
		// frm.set_query('unit', function (doc) {
		// 	let filters = []
		// 	if (frm.doc.property_name) {
		// 		filters.push(["Unit", "property", "in", frm.doc.property_name])
		// 	}
		// 	if (frm.doc.property_name) {
		// 		filters.push(["Unit", "status", "=", "Available"])
		// 	}
		// 	if (frm.doc.unit_type) {
		// 		filters.push(["Unit", "unit_type", "=", frm.doc.unit_type])
		// 	}
		// 	if (frm.doc.floor) {
		// 		filters.push(["Unit", "floor", "=", frm.doc.floor])
		// 	}
		// 	if (frm.doc.unit_nature) {
		// 		filters.push(["Unit", "unit_nature", "=", frm.doc.unit_nature])
		// 	}
		
		// 	return {
		// 		"filters": filters
		// 	};
		// })

		// frm.set_query('parking', function (doc) {
		// 	let filters = []
		// 	if (frm.doc.property_name) {
		// 		filters.push(["Unit", "property", "in", frm.doc.property_name])
		// 	}
		// 	if (frm.doc.property_name) {
		// 		filters.push(["Unit", "status", "=", "Available"])
		// 	}
		// 	if (frm.doc.property_name) {
		// 		filters.push(["Unit", "unit_nature", "=", "Parking"])
		// 	}
		// 	return {
		// 		"filters": filters
		// 	};
		// })
        prev_doc = frappe.get_prev_doc()
        
	},

    unit:function(frm){
        frappe.db.get_value("Unit",frm.doc.unit,["rent","monthly_rent"]).then(r =>{
			frm.set_value("yearly_rent",r.message.rent)
			frm.set_value("monthly_rent",r.message.monthly_rent)
		})
    },
    customer:function(frm){
        frappe.db.get_value("Customer",frm.doc.customer,["customer_name","custom_passport_no","custom_contact_no","email_id","custom_nationality","territory","custom_emirate_id"]).then(r =>{
			frm.set_value("tenant_name",r.message.customer_name)
			frm.set_value("passport_no",r.message.custom_passport_no)
            frm.set_value("contact_no",r.message.custom_contact_no)
            frm.set_value("email",r.message.email_id)
            frm.set_value("nationality",r.message.custom_nationality)
            frm.set_value("territory",r.message.territory)
            frm.set_value("custom_emirates_id",r.message.custom_emirate_id)

		})
    }
});

frappe.ui.form.on('Unit Details', {
	unit_details_remove:function(frm){
		calculate_yearly_rent(frm);
        calculate_total_unit_area(frm)
        
	},
    property: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        
        if (row.property) {
            frappe.db.get_value("Property", row.property, ["property_owner", "building_name"])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, "property_owner", r.message.property_owner);
                        frappe.model.set_value(cdt, cdn, "property_name", r.message.building_name);
                    }
                });
        }
    },

    unit: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.unit) {
            frappe.db.get_value("Unit", row.unit, ["carpet_area", "unit_type", "floor","rent", "unit_nature"])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, "unit_type", r.message.unit_type);
                        frappe.model.set_value(cdt, cdn, "sq_ft", r.message.carpet_area);
                        frappe.model.set_value(cdt, cdn, "floor", r.message.floor);
                        frappe.model.set_value(cdt, cdn, "rent_amount", r.message.rent);
                         frappe.model.set_value(cdt, cdn, "unit_nature", r.message.unit_nature);
                    }
                });
        }
    },

	rent_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // if (row.property && row.unit) {
            calculate_yearly_rent(frm);
        // }
    },
    
    unit_area_sqm: function(frm, cdt, cdn) {
        
        let row = locals[cdt][cdn];
        // if (row.property && row.unit) {
            calculate_total_unit_area(frm);
        // }
    }
	
	
});

function calculate_yearly_rent(frm) {
    let total = 0;

    (frm.doc.unit_details || []).forEach(row => {
        total += flt(row.rent_amount); 
    });

    frm.set_value("yearly_rent", total);
    frm.set_value("monthly_rent", flt(total/12))
}


frappe.ui.form.on('Charge Details', {
	type_of_charges_remove:function(frm){
		calculate_total_charges(frm);
        
	},
   
	amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.amount) {
            calculate_total_charges(frm);
        }
    }
	
});

function calculate_total_charges(frm) {
    let total = 0;

    (frm.doc.type_of_charges || []).forEach(row => {
        total += flt(row.amount); 
    });

    frm.set_value("total_charges", total);
}


function calculate_total_unit_area(frm) {
    let total = 0;

    (frm.doc.unit_details || []).forEach(row => {
        total += flt(row.unit_area_sqm); 
    });

    frm.set_value("total_area_sqmt", total);
}
