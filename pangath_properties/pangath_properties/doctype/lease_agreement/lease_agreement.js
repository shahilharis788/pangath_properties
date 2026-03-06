// Copyright (c) 2022, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lease Agreement', {
	before_save:function(frm){
		 frm.set_df_property('naming_series', 'hidden', 1);
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
            }
        
        
    },
	refresh: function (frm) {
       
        if (frm.doc.docstatus === 1) {
			frappe.call({
    							method: "pangath_properties.pangath_properties.doctype.lease_agreement.lease_agreement.create_customer",
    							args: {
										exist_cus : frm.doc.is_existing_customer,
										cust: frm.doc.tenant_name || "",
            							passport_no: frm.doc.passport_no || "",
            							contact_no: frm.doc.contact_no || "",
            							email: frm.doc.email || "",
            							nationality: frm.doc.nationality || "",
            							emirates_id: frm.doc.custom_emirates_id || "",
            							territory: frm.doc.territory || "",
            							tax_id: frm.doc.tax_id || "",
           	 							payment_terms: frm.doc.payment_terms_template || ""
        								
    							},
    						   callback: function (r) {
								 if(!frm.doc.is_existing_customer && r.message.status == "created"){
								 	frappe.show_alert({
               										 message: __('Customer Created Successfully: ') + r.message.cust,
                									 indicator: 'green'
            										});
								}
        
    							},
    							freeze: true,
    							freeze_message: __("Creating Customer...")
			});
            frm.add_custom_button("Tenancy Contract", async function () {
				
				frappe.call({
					method: "pangath_properties.pangath_properties.doctype.lease_agreement.lease_agreement.validate_contract_creation",
					args:{
						doc: frm.doc.name
					},
					callback:function(r){
						if(r.message == 1){
							frappe.throw("Booking is Already Linked With a Tenancy Contract")
						}
					}

				})
				
				try {
                    let addr = '';
                    let email = '';
                    let phone = '';
                    let eid = '';
                    let cus_name = '';

                    
                    const customer_res = await frappe.db.get_value("Customer", frm.doc.customer, [
                        "customer_primary_address",
                        "custom_emirate_id",
                        "customer_name"
                    ]);

                    if (customer_res.message) {
                        addr = customer_res.message.customer_primary_address;
                        eid = customer_res.message.custom_emirate_id;
                        cus_name = customer_res.message.customer_name;
                    }

                    
                    if (addr) {
                        const address_res = await frappe.db.get_value("Address", addr, [
                            "email_id",
                            "phone"
                        ]);

                        if (address_res.message) {
                            email = address_res.message.email_id;
                            phone = address_res.message.phone;
                        }
                    }
                    frappe.new_doc("Tenancy Contract", {
                        tenant_onboarding: frm.doc.lease_application || "",
                        issue_date: frm.doc.posting_date || "",
                        name_of_tenant: frm.doc.customer || frm.doc.tenant_name || "",
						customer_name: frm.doc.customer || frm.doc.tenant_name || "",
                        tenant_address: addr || "",
                        contact_no: phone || "",
                        email: email || "",
                        eid_no: eid || "",
                        customer_name: cus_name || "",
						contract_start_date: frm.doc.period_start_date || "",
						contract_end_date: frm.doc.period_end_date || "",
						unit_details: frm.doc.unit_details || "",
						//type_of_charges: frm.doc.type_of_charges || "",
						yearly_rent: frm.doc.yearly_rent || "",
						terms: frm.doc.terms || "",
						tc_name: frm.doc.tc_name || "",
						condition_inspection: frm.doc.condition_inspection,
						booking_agreement: frm.doc.name,
						total_area_sqmt: frm.doc.total_area_sqmt,
						tentative_hand_over_date: frm.doc.tentative_hand_over_date,
						agreement_term_date: frm.doc.agreement_term_date,
						contract_start_date: frm.doc.contract_start_date,
						fit_out_period: frm.doc.fit_out_period,
						contract_end_date: frm.doc.contract_end_date
                    });
                } catch (e) {
                    frappe.msgprint(__('Error creating Tenancy Contract: ') + e.message);
                    console.error(e);
                }
            });
        }
		if (!frm.is_new() && frm.doc.docstatus != 2) {

    frm.add_custom_button("Make Payment Entry", function () {

        // Check if Payment Entry already exists
        frappe.db.get_value(
            "Payment Entry",
            { custom_booking_agreement_reference: frm.doc.name },
            "name"
        ).then(r => {

            if (r.message && r.message.name) {

                frappe.throw(
                    __("Payment Entry already created: {0}", [r.message.name])
                );

            }

            // Check existing customer
            if (!frm.doc.is_existing_customer) {
                frappe.throw(
                    __("<b>{0}</b> is not an existing Customer. Please create/select a Customer before making Payment Entry.",
                    [frm.doc.tenant_name])
                );
            }

            // Create Payment Entry
            frappe.call({
                method: "pangath_properties.pangath_properties.doctype.lease_agreement.lease_agreement.create_payment_entry",
                args: {
                    lease_agreement: frm.doc.name
                },
                callback: function (r) {

                    if (r.message) {

                        frappe.show_alert({
                            message: __("Payment Entry Created: {0}", [r.message]),
                            indicator: "green"
                        });
						frappe.set_route("Form", "Payment Entry", r.message);
                    }

                }
            });

        });

    });

}

    },
	
	lease_application: function (frm) {
		//set_html(frm);
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
		 frm.set_query("bank_account", function() {
            return {
                filters: {
                    is_company_account: 1
                }
            };
        });
		frm.set_query("paid_from", function() {
        return {
            filters: {
                account_type: "Receivable"
            }
        };
    });
	frm.set_query("paid_to", function() {
    return {
        filters: {
            account_type: ["in", ["Bank", "Cash"]]
        }
    };
});
	},

	tc_name: function (frm) {
		if (frm.doc.tc_name && frm.doc.lease_application) {
			frappe.db.get_doc('Tenant Onboarding', frm.doc.lease_application)
				.then(l_app_doc => {
					return frappe.call({
						method: 'erpnext.setup.doctype.terms_and_conditions.terms_and_conditions.get_terms_and_conditions',
						args: {
							template_name: frm.doc.tc_name,
							doc: l_app_doc
						},
						callback: function (r) {
							frm.set_value('terms', r.message)
						}
					});
				})
		}
	},
});


var set_html = function (frm) {
	if (frm.doc.lease_application) {
		frappe.db.get_doc('Tenant Onboarding', frm.doc.lease_application)
			.then(doc => {
				let lease_html = `
				<div class="frugal-card">
					<table style="width:100% "><br>
						<tr height="30px">
							<td style="width:15%; text-align: left;">Customer</td>
							<td style="width:5%;">-</td>
							<td style="width:15%;text-align: right;"><b>${doc.customer}</b></td>
							<td style="width:5%;"></td>
							<td style="width:20%; text-align: left;">Company</td>
							<td style="width:5%;">-</td>
							<td style="width:15%; text-align:right;text-align: right;"><b>${doc.company}</b></td>
							<td style="width:10%;"></td>
						</tr>
						<tr height="30px">
							<td style="width:15%; text-align: left;">Unit</td>
							<td style="width:5%;">-</td>
							<td style="width:15%;text-align: right;"><b>${doc.unit}</b></td>
							<td style="width:5%;"></td>
							<td style="width:20%; text-align: left;">Postind Date</td>
							<td style="width:5%;">-</td>
							<td style="width:15%; text-align:right;text-align: right;"><b>${doc.posting_date}</b></td>
							<td style="width:10%;"></td>
						</tr>
						<tr height="30px">
							<td style="width:15%; text-align: left;">Period Start Date</td>
							<td style="width:5%;">-</td>
							<td style="width:15%;text-align: right;"><b>${doc.period_start_date}</b></td>
							<td style="width:5%;"></td>
							<td style="width:20%; text-align: left;">Period End Date</td>
							<td style="width:5%;">-</td>
							<td style="width:15%; text-align:right;text-align: right;"><b>${doc.period_end_date}</b></td>
							<td style="width:10%;"></td>
						</tr>
						<tr height="30px">
							<td style="width:15%; text-align: left;">Period</td>
							<td style="width:5%;">-</td>
							<td style="width:15%;text-align: right;"><b>${doc.period}</b></td>
							<td style="width:5%;"></td>
							<td style="width:20%; text-align: left;">Payment Amount</td>
							<td style="width:5%;">-</td>
							<td style="width:15%; text-align:right;text-align: right;"><b>${doc.payment_amount}</b></td>
							<td style="width:10%;"></td>
						</tr>
						<tr height="30px">
							<td style="width:15%; text-align: left;">Payment frequency</td>
							<td style="width:5%;">-</td>
							<td style="width:15%;text-align: right;"><b>${doc.payment_frequency}</b></td>
							<td style="width:5%;"></td>
							<td style="width:20%; text-align: left;">Total</td>
							<td style="width:5%;">-</td>
							<td style="width:15%; text-align:right;text-align: right;"><b>${doc.total}</b></td>
							<td style="width:10%;"></td>
						</tr>
					</table>
				</div><br>`
				lease_html += `
				<div>
					<table style = "border: 1px solid grey;">
						<tr height="30px" style = "border: 1px  grey;">
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Payment Scheduled Date</td>
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Payment Amount</td>
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Mode Of Payment</td>
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Cheque Reference Number</td>
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Cheque Reference Date</td>
							<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px">Paid Amount</td>
						</tr>`

				doc.payment_schedule.forEach((i) => {
					lease_html += `
					<tr height="30px">
						<td style="width:15%; text-align: left; border: 1px solid grey;padding:10px"><b>${i.payment_scheduled_date}</b></td>
						<td style="width:15%; text-align: right; border: 1px solid grey;padding:10px"><b>${i.payment_amount}</b></td>
						<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px"><b>${i.mode_of_payment ? i.mode_of_payment : ''}</b></td>
						<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px"><b>${i.reference_number ? i.reference_number : ''}</b></td>
						<td style="width:15%; text-align: left; border: 1px solid grey; padding:10px"><b>${i.reference_date ? i.reference_date : ''}</b></td>
						<td style="width:15%; text-align: right; border: 1px solid grey; padding:10px"><b>${i.paid_amount}</b></td>
					</tr>`
				});

				lease_html += `</table></div>`
				frm.fields_dict.lease_agreement_details.html(lease_html);
			})
	} else {
		frm.fields_dict.lease_agreement_details.html('');
	}
};

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
		else{
             frappe.model.set_value(cdt, cdn, "unit_type", "");
             frappe.model.set_value(cdt, cdn, "sq_ft", "");
             frappe.model.set_value(cdt, cdn, "floor", "");
             frappe.model.set_value(cdt, cdn, "rent_amount", "");
             frappe.model.set_value(cdt, cdn, "unit_nature", "");

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
	if(frm.doc.doctype == "Lease Agreement"){
    	frm.set_value("monthly_rent", flt(total/12))
	}
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
