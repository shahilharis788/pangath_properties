frappe.ui.form.on("Payment Entry", {
	onload_post_render(frm) {
		console.log('ifoj')
		if (frappe.get_prev_route()[1] == "Tenant Onboarding") {
			if (frm.doc.tenant_onboarding && frm.doc.status_je == 'Paid') {
				frm.trigger("party");
				frm.trigger("mode_of_payment");
			}
			if (frm.doc.tenant_onboarding && frm.doc.status_je == 'PDC Created') {
				frm.trigger("party");
				frm.trigger("mode_of_payment");
			}
		}
	},

	onload: function (frm) {
		if(frm.doc.__islocal){
			$.each(frm.doc.references, function(i, ref){
				frappe.call({
					"method": "pangath_properties.events.payment_entry.get_refernce",
					"args": {
						'ref': ref.reference_name
					},
					callback: function (r) {
						console.log('igri')
						if(r.message.doctype == "TC Payment Schedule"){
							frm.set_value("reference_no",r.message.cheque_number)
							frm.set_value("reference_date",r.message.cheque_date)
							frm.set_value("cheque_issue_date",r.message.date_of_issue)
						}
						if(r.message.doctype == "Type Of Charges"){
							frm.set_value("reference_no",r.message.reference_number)
							frm.set_value("reference_date",r.message.reference_date)
							frm.set_value("cheque_issue_date",r.message.issue_date)
						}
					}
				});
			})
		}

		frm.set_query('reference_doctype','references', function () {
			return {
				filters: {
					"name": ["in",["Sales Order","Sales Invoice", "Journal Entry", "Dunning", "Tenant Onboarding Termination"]],
				}
			}
		}),
		frm.set_query('unit', function (doc) {
			let filters = []
			return {
				"filters": filters
			};
		})
		frm.set_query('customer', function (doc) {
			let filters = []
			return {
				"filters": filters
			};
		})
	},
});

frappe.ui.form.on('Payment Entry Reference', {
	references_add: function (frm, cdt, cdn) {
		if (frm.doc.tenant_onboarding && frm.doc.status_je == 'PDC Created') {
			frm.fields_dict['references'].grid.get_field('reference_name').get_query = function (frm) {
				var je_list = [];
				$.each(frm.references, function (idx, val) {
					if (val.reference_name) {
						je_list.push(val.reference_name);
					}
				});
				let row = locals[cdt][cdn];
				if (row.reference_doctype == 'Journal Entry') {
					return {
						filters: [
							['Journal Entry', 'name', 'not in', je_list],
							['Journal Entry', 'docstatus', '=', 1],
							['Journal Entry', 'tenant_onboarding', '=', frm.tenant_onboarding],
							['Journal Entry', 'pe_created', '=', 0],
							['Journal Entry', 'status', '=', 'PDC Created']
						]
					};
				}
			};
		}
		if (frm.doc.tenant_onboarding && frm.doc.status_je == 'Paid') {
			frm.fields_dict['references'].grid.get_field('reference_name').get_query = function (frm) {
				var je_list = [];
				$.each(frm.references, function (idx, val) {
					if (val.reference_name) {
						je_list.push(val.reference_name);
					}
				});
				let row = locals[cdt][cdn];
				if (row.reference_doctype == 'Journal Entry') {
					return {
						filters: [
							['Journal Entry', 'name', 'not in', je_list],
							['Journal Entry', 'docstatus', '=', 1],
							['Journal Entry', 'tenant_onboarding', '=', frm.tenant_onboarding],
							['Journal Entry', 'pe_created', '=', 0],
							['Journal Entry', 'status', '=', 'Paid']
						]
					};
				}
			};
		}
	},
});