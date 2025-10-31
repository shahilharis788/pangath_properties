// Copyright (c) 2025, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Proposal Agreement', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Tenancy contract'),function () {
				let args = {
					'name': frm.doc.name,
						'customer': frm.doc.customer,
						'building': frm.doc.building,
						'unit' : frm.doc.unit,
						'name' : frm.doc.name,
						'total' :frm.doc.total
				}
				frappe.call({
					'method': 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.create_tenancy_contract',
					'args': {"args": args},
					callback: function (r) {
						if (r && r.message) {
							frappe.set_route('Form', 'Tenancy Contract', r.message);
						}
					}
				});
			}, __('Create'));
			cur_frm.add_custom_button(__('Payment Entry (Auto)'), () => {
				frappe.call({
						method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.auto_create_payment_entry',
						args: { 'docname': frm.doc.name },
						callback: function(r) {
							var doc = frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
					});
								}, __('Create'));

			cur_frm.add_custom_button(__('Payment Entry (Paid)'), () => {
				frappe.call({
						method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.create_payment_entry',
					args: { 'doc': frm.doc },
					callback: function(r) {
						var doc = frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				});
			}, __('Create'));
			cur_frm.add_custom_button(__('Payment Entry (PDC Created)'), () => {
				return frappe.call({
					method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.create_payment_entry_pdc_created',
					args: { 'doc': frm.doc },
					callback: function(r) {
						var doc = frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				});
			}, __('Create'));
			// cur_frm.add_custom_button(__('Create PDC Reconciliation'), () => {
			// 		new_doc=frappe.new_doc("PDC Register")
			// 		frappe.set_route("Form","PDC Register",new_doc)
			// }, __('Create'));
			if(frm.doc.status != "Terminated"){
			cur_frm.add_custom_button(__('Tenant Onboarding'), () => {
				let d = new frappe.ui.Dialog({
					title: 'Cancellation Details',
					fields: [
						{
							label: 'Cancellation Date',
							fieldname: 'cancellation_date',
							fieldtype: 'Date'
						},
					],
					size: 'small', // small, large, extra-large
					primary_action_label: 'Submit',
					primary_action(values) {
						d.hide();
						if(values.cancellation_date < frm.doc.period_start_date){
							frappe.throw("Cancellation Date Should be After Period Starting Date")
						}
						else if(values.cancellation_date > frm.doc.period_end_date){
							frappe.throw("Cancellation Date Should be before Period Ending Date")
						}
						else{
						return frappe.call({
							method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.cancel_tenant_onboarding',
							args: { 'doc': frm.doc,
									'values': values.cancellation_date },
							callback: function(r) {
								if (r && r.message) {
									frappe.set_route('Form', 'Tenant Onboarding Termination', r.message);
								}
							}
						});
					}
					}
				});
				d.show();
			}, __('Terminate'));
		}

			cur_frm.add_custom_button(__('Tenant Onboarding'), () => {
				return frappe.call({
					method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.renew_tenant_onboarding',
					args: { 'doc': frm.doc },
					callback: function(r) {
						if (r && r.message) {
							var doc = frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
						}
					}
				});
			}, __('Renew'));
		}
		// hide + icon of  Task from connection 
		setTimeout(() => {
			$("[data-doctype='Payment Entry']").find("button").hide();
			}, 10);
	},
	payment_amount: function(frm) {
		if (frm.doc.payment_amount) {
			frm.set_value('monthly_rent', frm.doc.payment_amount / 12);
		}
	},
	period: function(frm) {
		if (frm.doc.period == 'Month') {
			frm.set_value('payment_frequency','Monthly');
		}
	},
	onload: function (frm) {
		frm.set_query('unit', function (doc) {
			let filters = [["Unit", "status", "=", "Available"]]
			if (frm.doc.building) {
				filters.push(["Unit", "property", "in", frm.doc.building])
			}
			return {
				"filters": filters
			};
		})
		frm.set_query("account_paid_to", "payment_schedule", function() {
			return {
			filters: [
				['Account', 'account_type', 'in', 'Bank, Cash, Receivable'],
				['Account', 'is_group', '=', 0],
				['Account', 'company', '=', frm.doc.company]
			]
			};
		});
		frm.set_query("account_paid_to", "type_of_charges", function() {
			return {
			filters: [
				['Account', 'account_type', 'in', 'Bank, Cash, Receivable'],
				['Account', 'is_group', '=', 0],
				['Account', 'company', '=', frm.doc.company]
			]
			};
		});
	},
	building: function(frm) {
		frm.set_value("unit", "");
	}
});

frappe.ui.form.on('LA Repayment Schedule', {
	payment_schedule_add: function(frm,cdt,cdn) {
		frappe.model.set_value(cdt, cdn, 'mode_of_payment', frm.doc.mode_of_payment);
	},
	reference_date: function(frm,cdt,cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'cheque_end_date', frappe.datetime.add_months(row.reference_date, 6));
	},
	add_remarks: function(frm,cdt,cdn) {
		let row = locals[cdt][cdn];
		let d = new frappe.ui.Dialog({
			title: 'Remarks',
			fields: [
				{
					label: 'Remarks',
					fieldname: 'remarks_add',
					fieldtype: 'Small Text'
				},
			],
			primary_action_label: 'Add',
			primary_action(values) {
				frappe.call({
					method: 'pangath_properties.pangath_properties.doctype.proposal_agreement.proposal_agreement.cheque_status',
					args:{
						"pay_ref": row.name,
						"to_name": frm.doc.name,
						"pay_date":row.reference_date,
						"date": frappe.datetime.now_date(),
						"status": row.status,
						"remarks": values.remarks_add,
						"ref_no":row.reference_number
					},
					callback: function (r) {
						if (r && r.message) {
							set_html(frm, r.message, cdt, cdn)
							frappe.model.set_value(cdt, cdn, "remarks", JSON.stringify(r.message));
							frm.refresh()
						}
					}
				});
				d.hide();
		}
		});
		d.show();
	},
	mode_of_payment:function(frm,cdt,cdn){
		let row =locals[cdt][cdn]
		frappe.db.get_doc('Mode of Payment', row.mode_of_payment)
		.then(doc => {
			doc.accounts.forEach(i => {
				if(i.company == frm.doc.company){
					if(i.default_account){
						frappe.model.set_value(row.doctype,row.name,'account_paid_to',i.default_account)
				}
			}
			})

		})

	}
});
frappe.ui.form.on('Type Of Charges', {
	add_remarks: function(frm,cdt,cdn) {
		let row = locals[cdt][cdn];
		let d = new frappe.ui.Dialog({
			title: 'Remarks',
			fields: [
				{
					label: 'Remarks',
					fieldname: 'remarks_add',
					fieldtype: 'Small Text'
				},
			],
			primary_action_label: 'Add',
			primary_action(values) {
				let remarks_list = [];
				if (row.remarks) {
					remarks_list = JSON.parse(row.remarks)
				}
				if (values) {
					let remarks_dict = {
					'date' :frappe.datetime.now_date(),
					'status' : row.status,
					'remarks': values.remarks_add
					};
					remarks_list.push(remarks_dict );
				  }
				  frappe.model.set_value(cdt, cdn, "remarks", JSON.stringify(remarks_list));
				  set_html(frm, remarks_list, cdt, cdn)
			d.hide();
				d.hide();
		}
		});
		d.show();
	},
	mode_of_payment:function(frm,cdt,cdn){
		let row =locals[cdt][cdn]
		frappe.db.get_doc('Mode of Payment', row.mode_of_payment)
		.then(doc => {
			doc.accounts.forEach(i => {
				if(i.company == frm.doc.company){
					if(i.default_account){
						frappe.model.set_value(row.doctype,row.name,'account_paid_to',i.default_account)
				}
			}
			})
		})
	}
});

var set_html = function(frm, remarks, cdt, cdn) {
	var remarks_html = `<table border="1px grey"  bordercolor="grey" style="width: 100%; height:100">
	<tr style="height: 15px;">
	<td style="text-align: center; color:#687178; width:10%">Date</td>
	<td style="text-align: center; color:#687178; width:10%">Status</td>
	<td style="text-align: center; color:#687178; width:80%">Remarks</td>
  </tr>`
if(remarks){
	$.each(remarks, function (k, rem) {
		remarks_html += `<tbody><tr>`;
		remarks_html += `<td style="text-align: left; background-color:#FFFF; font-size: 12px;">` + rem.date+ "</td>";
		remarks_html += `<td style="text-align: left; background-color:#FFFF; font-size: 12px;">` + rem.status + "</td>";
		remarks_html += `<td style="text-align: left; background-color:#FFFF; font-size: 12px;">` + rem.remarks + "</td>";
		remarks_html += `</tr></tbody>`;
  });
}
remarks_html = remarks_html + `</table>`;
frappe.model.set_value(cdt, cdn,"remarkss",remarks_html);
}


frappe.ui.form.on("Type Of Charges",{
	particulars:function(frm,cdt,cdn){
		let row=locals[cdt][cdn]
		frappe.db.get_doc("Particulars",row.particulars)
			.then((doc) => {
				if(doc.accounts.length && doc.accounts.length > 0){
					doc.accounts.forEach(i => {
							if(i.company == frm.doc.company){
								if(i.default_account){
									frappe.model.set_value(row.doctype,row.name,'account',i.default_account)
							}
						}
					});
				}
				else{
					frappe.model.set_value(row.doctype,row.name,'account','')
				}
			});
	}
})
