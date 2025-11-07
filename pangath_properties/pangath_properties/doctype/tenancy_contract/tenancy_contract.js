// Copyright (c) 2023, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenancy Contract', {
	
	
	refresh:function(frm){
		filters(frm)
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Move-Out'),function () {
				frappe.model.open_mapped_doc({
					method: "pangath_properties.pangath_properties.doctype.tenancy_contract.tenancy_contract.create_condition_inspection",
					frm:frm
				})
			});
			frm.add_custom_button(__('Renew'),function () {
				frappe.model.open_mapped_doc({
					method: "pangath_properties.pangath_properties.doctype.tenancy_contract.tenancy_contract.renew_tenancy_contract",
					frm:frm
				})
			});
			frm.add_custom_button(__('Quotation'),function () {
				frappe.model.open_mapped_doc({
					method: "pangath_properties.pangath_properties.doctype.tenancy_contract.tenancy_contract.create_quotation",
					frm:frm
				})
			});
		}

		frm.fields_dict['type_of_charges'].grid.get_field('item_tax_template').get_query = function(cdt, cdt, cdn){
		    var child = locals[cdt][cdn]
		    return {
		        filters:[
		        ['company','=',frm.doc.company]
		        ]
		    }
		}
		
		
			frm.fields_dict['payment_schedule'].grid.get_field('item_tax_template').get_query = function(cdt, cdt, cdn){
		    var child = locals[cdt][cdn]
		    return {
		        filters:[
		        ['company','=',frm.doc.company]
		        ]
		    }
		}
		
		frm.fields_dict['schedule_payments'].grid.get_field('item_tax_template').get_query = function(cdt, cdt, cdn){
		    var child = locals[cdt][cdn]
		    return {
		        filters:[
		        ['company','=',frm.doc.company]
		        ]
		    }
		}
		

	},
	tc_name: function (frm) {
		if (frm.doc.tc_name)
		{
		return frappe.call({
			method: 'erpnext.setup.doctype.terms_and_conditions.terms_and_conditions.get_terms_and_conditions',
			args: {
			  template_name: frm.doc.tc_name,
			  doc: frm.doc
			},
			callback: function(r) {
				frm.set_value('terms', r.message)
			}
		  });
		}
	},
	onload: function(frm) {
		frm.fields_dict.unit_details.grid.get_field('unit').get_query = function(doc, cdt, cdn) {
            let child = locals[cdt][cdn];
            return {
                filters: {
                    property: child.property
                }
            };
        };

		let prev_doc = frappe.get_prev_route();
		let prev_doc_type = prev_doc[1];
		let prev_doc_name = prev_doc[2];
		if(frm.doc.yearly_rent){
			frm.set_value("m_rent", flt(frm.doc.yearly_rent/12))
		}
		
		if (prev_doc_type === "Lease Agreement") {
			frappe.db.get_doc(prev_doc_type, prev_doc_name).then(doc => {
				if (doc.type_of_charges && doc.type_of_charges.length > 0) {
					doc.type_of_charges.forEach(row => {
						let toc = frm.add_child("type_of_charges");
						toc.particulars = row.particulars;
						toc.amount = row.amount;
					});
					frm.refresh_field("type_of_charges");
				}
			});
		}
		frm.set_query("cost_center", function() {
			return {
			"filters": {
			'company':frm.doc.company
			}
			};
			});

			// frm.set_query("unit_number", function() {
			// 	return {
			// 	"filters": {
			// 	"property": frm.doc.property_name,
			// 	'company':frm.doc.company
			// 	}
			// 	};
			// });

			frm.fields_dict.payment_schedule.grid.get_field('mode_of_payment').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];

            if (row.is_pdc) {
                return {
                    filters: {
                        is_pdc: 1
                    }
                };
            } else {
                return {
                    filters: {
                        is_pdc: 0
                    }
                };
            }
        };
	},
	'property_name':function(frm){
		// frm.set_query("unit_number", function() {
		// 	return {
		// 	"filters": {
		// 	"property": frm.doc.property_name,
		// 	'company':frm.doc.company
		// 	}
		// 	};
		// 	});
			frm.set_query("cost_center", function() {
				return {
				"filters": {
				'company':frm.doc.company
				}
				};
				});
			},
	'validate': function(frm) {
		frm.set_value('grand_total',frm.doc.total_taxes_and_charges+ frm.doc.total )
	},
	
});


var filters = (frm) =>{
	frm.set_query("property_name", function() {
		return {
		"filters": {
		"company": frm.doc.company,
		}
		};
		});
		
}

frappe.ui.form.on('Unit Details', {
	unit_details_remove:function(frm){
		calculate_yearly_rent(frm);
        
	},
    property: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        
        if (row.property) {
            frappe.db.get_value("Property", row.property, "property_owner")
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, "property_owner", r.message.property_owner);
                    }
                });
        }
    },

    unit: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.unit) {
            frappe.db.get_value("Unit", row.unit, ["carpet_area", "unit_type"])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, "unit_type", r.message.unit_type);
                        frappe.model.set_value(cdt, cdn, "sq_ft", r.message.carpet_area);
                    }
                });
        }
    },

	rent_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
       	calculate_yearly_rent(frm);
        
    }
	
	
});

function calculate_yearly_rent(frm) {
    let total = 0;

    (frm.doc.unit_details || []).forEach(row => {
        total += flt(row.rent_amount); 
    });

    frm.set_value("yearly_rent", total);
	frm.set_value("m_rent", flt(total/12))
}

frappe.ui.form.on('TA Payment Schedule', {
    number_of_period: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);

        if (row.number_of_period > 1) {
            frm.set_value('custom_number_of_period', row.number_of_period);
			
        }
    }
});
