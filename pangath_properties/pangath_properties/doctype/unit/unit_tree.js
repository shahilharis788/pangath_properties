frappe.treeview_settings['Unit'] = {
	breadcrumb: "Real Estate",
	add_tree_node: "real_estate.real_estate.doctype.unit.unit.add_node",
	get_tree_nodes: "real_estate.real_estate.doctype.unit.unit.get_children",
	get_tree_root: true,
	root_label: "Unit",

	filters: [{
		fieldname: "company",
		fieldtype: "Select",
		options: erpnext.utils.get_tree_options("company"),
		label: __("Company"),
		default: erpnext.utils.get_tree_default("company")
	}],

	fields: [
		{ fieldtype: 'Data', fieldname: 'unit_no', label: __('Unit No'), reqd: true },
		{ fieldtype: 'Link', options: 'Property', fieldname: 'property', label: __('Property'), reqd: true },
		{ fieldtype: 'Check', fieldname: 'is_group', label: __('Group Node'), description: __("Child nodes can be only created under 'Group' type nodes") },
		{ fieldtype: 'Select', options: '\nAvailable\nLeased\nBooked\nSold\nNot Hand Over', fieldname: 'status', label: __('Status'), reqd: true },
		{ fieldtype: 'Data', fieldname: 'custom_current_owner', label: __('Current Owner'), reqd: true },
		{ fieldtype: 'Link', options: 'Floor', fieldname: 'floor', label: __('Floor'), reqd: true },
		{ fieldtype: 'Select', options: '\nResidential - Rental\nResidential - Sale\nCommercial\nParking', fieldname: 'unit_nature', label: __('Unit Nature'), reqd: true },
	],

	get_label: function (node) {
		console.log(node);
		const label = frappe.utils.escape_html(node.label || "");
		const status = node.data?.status ? `(${frappe.utils.escape_html(node.data.status)})` : "";

		let debit = node.data?.debit || 0;
		let credit = node.data?.credit || 0;
		let balance = node.data?.balance || 0;

		// If node is a parent and has children, sum child values
		if (node.children && node.children.length > 0) {
			debit = node.children.reduce((sum, child) => sum + (child.data?.debit || 0), 0);
			credit = node.children.reduce((sum, child) => sum + (child.data?.credit || 0), 0);
			balance = node.children.reduce((sum, child) => sum + (child.data?.balance || 0), 0);
		}

		const debit_fmt = frappe.format(debit, { fieldtype: "Currency" });
		const credit_fmt = frappe.format(credit, { fieldtype: "Currency" });

		let balance_label = "";
		let balance_value = balance;

		if (balance > 0) {
			balance_label = __("Dr");
		} else if (balance < 0) {
			balance_label = __("Cr");
			balance_value = Math.abs(balance);
		}

		const balance_fmt = frappe.format(balance_value, { fieldtype: "Currency" });

		return `
			<table style="width: 100%; table-layout: fixed; font-size: 90%;">
				<tr>
					<td style="width: 60%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
						<strong>${label}</strong>
						${status ? `<span style="margin-left: 8px; color: #888;">${status}</span>` : ""}
					</td>
					<td style="width: 50%; text-align: right; color: #888; white-space: nowrap; display: flex">
						${debit_fmt} ${__('Dr')} &nbsp;&nbsp;&nbsp;
						${credit_fmt} ${__('Cr')}  &nbsp;&nbsp;&nbsp;
						
						${balance_fmt} ${balance_label}
					</td>
				</tr>
			</table>
		`;
	},
	toolbar: [
		{
			label: __("Add Child"),
			condition: function (node) {
				return (
					frappe.boot.user.can_create.includes("Unit") &&
					node.expandable &&
					!node.hide_add &&
					!node.is_root
				);
			},
			click: function () {
				frappe.views.trees["Unit"].new_node();
			},
			btnClass: "hidden-xs",
		},
		{
			label: __("View Ledger"),
			condition: function (node) {
				return !node.root && frappe.boot.user.can_read.includes("GL Entry");
			},
			click: function (node) {
				frappe.route_options = {
					from_date: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
					to_date: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
					company: frappe.treeview_settings["Unit"].treeview.page.fields_dict.company.get_value(),
					unit: node.label,
				};
				frappe.set_route("query-report", "General Ledger");
			},
			btnClass: "hidden-xs",
		}
	],

	extend_toolbar: true,

	post_render: function (treeview) {
		frappe.treeview_settings["Unit"].treeview = treeview;
	}
};
// };



