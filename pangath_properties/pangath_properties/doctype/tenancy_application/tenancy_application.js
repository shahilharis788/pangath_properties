// Copyright (c) 2025, iterative and contributors
// For license information, please see license.txt


frappe.ui.form.on('Tenancy Application', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
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
            frm.add_custom_button(__('Booking Agreement'),function () {
                frappe.model.open_mapped_doc({
                    method: "pangath_properties.pangath_properties.doctype.tenancy_application.tenancy_application.create_booking_agreement",
                    frm:frm,
                    args:{

                    }
                })
			},__('Create'));
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
		frm.set_query('unit', function (doc) {
			let filters = []
			if (frm.doc.property_name) {
				filters.push(["Unit", "property", "in", frm.doc.property_name])
			}
			if (frm.doc.property_name) {
				filters.push(["Unit", "status", "=", "Available"])
			}
			if (frm.doc.unit_type) {
				filters.push(["Unit", "unit_type", "=", frm.doc.unit_type])
			}
			if (frm.doc.floor) {
				filters.push(["Unit", "floor", "=", frm.doc.floor])
			}
			if (frm.doc.unit_nature) {
				filters.push(["Unit", "unit_nature", "=", frm.doc.unit_nature])
			}
		
			return {
				"filters": filters
			};
		})

		frm.set_query('parking', function (doc) {
			let filters = []
			if (frm.doc.property_name) {
				filters.push(["Unit", "property", "in", frm.doc.property_name])
			}
			if (frm.doc.property_name) {
				filters.push(["Unit", "status", "=", "Available"])
			}
			if (frm.doc.property_name) {
				filters.push(["Unit", "unit_nature", "=", "Parking"])
			}
			return {
				"filters": filters
			};
		})
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
