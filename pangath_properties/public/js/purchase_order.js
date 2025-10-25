frappe.ui.form.on("Purchase Order",{
    onload: function(frm) {
		setTimeout(() => {
			frm.set_query('unit', function (doc) {
				let filters = []
				return {
					"filters": filters
				};
			})
		}, 1000);
    }
})