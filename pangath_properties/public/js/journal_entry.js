frappe.ui.form.on("Journal Entry", {
	onload: function (frm) {
		setTimeout(() => {
			frm.set_query('unit','accounts', function (doc) {
				let filters = []
				return {
					"filters": filters
				};
			})
			frm.set_query('customer','accounts', function (doc) {
				let filters = []
				return {
					"filters": filters
				};
			})
		}, 1000);
		
	}
});


frappe.ui.form.on('Journal Entry', {
	onload: function (frm) {
		frm.add_custom_button('Unit/Property Wise Entry', function () {
			let d = new frappe.ui.Dialog({
				title: 'Insert Records',
				fields: [

					{
						label: 'Accounts Table',
						fieldname: 'accounts_table',
						fieldtype: 'Table',
						in_place_edit: true,
						fields: [
							{
								fieldtype: 'Link',
								label: 'Account',
								fieldname: 'account',
								options: 'Account',
								reqd: 1,
								in_list_view: 1,
								columns: 2,
								get_query: () => {
									return {
										filters: {
											'is_group': 0,
											'company': frm.doc.company
										}
									};
								},
							},
							{
								fieldtype: 'Select',
								label: 'Entry For',
								fieldname: 'entry_for',
								options: ['Unit', 'Property'],
								in_list_view: 1,
								columns: 2
							},
							{
								fieldtype: 'Link',
								label: 'Unit',
								fieldname: 'unit',
								options: 'Unit',
								in_list_view: 1,
								columns: 2,
								read_only_depends_on: 'eval:doc.entry_for=="Property"',
								get_query: () => {
									return {
										filters: {
											'is_group': 1
										}
									};
								},
							},
							{
								fieldtype: 'Link',
								label: 'Property',
								fieldname: 'property',
								options: 'Property',
								in_list_view: 1,
								columns: 2,
								read_only_depends_on: 'eval:doc.entry_for=="Unit"',
							},
							{
								fieldtype: 'Currency',
								label: 'Debit',
								fieldname: 'debit_in_account_currency',
								in_list_view: 1,
								columns: 1
							},
							{
								fieldtype: 'Currency',
								label: 'Credit',
								fieldname: 'credit_in_account_currency',
								in_list_view: 1,
								columns: 1
							}
						],
					}],
				
				primary_action(values) {
					console.log(values);
					frm.clear_table('accounts');
					frappe.call({
						method: 'pangath_properties.events.journal_entry.get_units_r_proty',
						args: {
							data: values.accounts_table
						},
						callback: function (r) {
							console.log(r);
							r.message.forEach(row => {
						let child = frm.add_child('accounts', row);
					});
					frm.refresh_field('accounts')
						}
					})

					d.hide();
				}
			
			});
			d.show();
		});
	},

});
