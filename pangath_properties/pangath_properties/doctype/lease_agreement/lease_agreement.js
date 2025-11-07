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
            frm.add_custom_button("Tenancy Contract", async function () {
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
								 if(!frm.doc.is_existing_customer && r.messages.status == "created"){
								 	frappe.show_alert({
               										 message: __('Customer Created Successfully: ') + r.message,
                									 indicator: 'green'
            										});
								}
        
    							},
    							freeze: true,
    							freeze_message: __("Creating Customer...")
				});
					
					
                    frappe.new_doc("Tenancy Contract", {
                        tenant_onboarding: frm.doc.lease_application || "",
                        issue_date: frm.doc.posting_date || "",
                        name_of_tenant: frm.doc.customer || "",
                        tenant_address: addr || "",
                        contact_no: phone || "",
                        email: email || "",
                        eid_no: eid || "",
                        customer_name: cus_name || "",
						contract_start_date: frm.doc.period_start_date || "",
						contract_end_date: frm.doc.period_end_date || "",
						unit_details: frm.doc.unit_details || "",
						type_of_charges: frm.doc.type_of_charges || "",
						yearly_rent: frm.doc.yearly_rent || "",
						terms: frm.doc.terms || "",
						tc_name: frm.doc.tc_name || "",
						condition_inspection: frm.doc.condition_inspection,
                    });
                } catch (e) {
                    frappe.msgprint(__('Error creating Tenancy Contract: ') + e.message);
                    console.error(e);
                }
            });
        }
    },
	lease_application: function (frm) {
		set_html(frm);
	},

	onload: function (frm) {
		set_html(frm);
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