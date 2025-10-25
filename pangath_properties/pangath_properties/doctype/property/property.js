// Copyright (c) 2022, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property', {
	onload: function(frm) {
		frm.fields_dict.details_html.html("");
		if (!frm.doc.__islocal) {
			frappe.call({
				method: "pangath_properties.pangath_properties.doctype.property.property.fetch_unit_details",
				args: {
					name: frm.doc.name
				},
				callback: (response) => {
					let data = response.data[0];
					if (frm.doc.no_of_units != data.unit_number) {
						frappe.model.set_value(frm.doc.doctype, frm.doc.name, "no_of_units", data.unit_number)
						frm.save()
					}
					set_html(frm, data)
				}
			});
		}
	}
})


let set_html = function(frm, data) {
    let building_html = `
	<style>
		.frugal-card {
			box-shadow: 3px 4px 8px 0 rgba(0, 0, 4, 0.1);
			width: 100%;
		}
	</style>
	<div class="frugal-card">
		<table style="width:100% "><br>
			<tr height="30px">
				<td style="width:10%;"></td>
				<td style="width:15%; text-align: left;">Total Units</td>
				<td style="width:5%;">-</td>
				<td style="width:15%;text-align: right;"><b>${data.unit_number}</b></td>
				<td style="width:5%;"></td>
				<td style="width:20%; text-align: left;">Vacant Units</td>
				<td style="width:5%;">-</td>
				<td style="width:15%; text-align:right;text-align: right;"><b>${data.available_units}</b></td>
				<td style="width:10%;"></td>
			</tr>
			<tr height="30px">
				<td style="width:10%;"></td>
				<td style="width:15%; text-align: left;">Rented Units</td>
				<td style="width:5%;">-</td>
				<td style="width:15%;text-align: right;"><b>${data.rented_units}</b></td>
				<td style="width:5%;"></td>
				<td style="width:20%; text-align: left;">Purchase Price</td>
				<td style="width:5%;">-</td>
				<td style="width:15%; text-align:right;text-align: right;"><b>${data.purchase_price}</b></td>
				<td style="width:10%;"></td>
			</tr>
			<tr height="30px">
				<td style="width:10%;"></td>
				<td style="width:15%; text-align: left;">Leased Units</td>
				<td style="width:5%;">-</td>
				<td style="width:15%;text-align: right;"><b>${data.leased_units}</b></td>
				<td style="width:5%;"></td>
				<td style="width:20%; text-align: left;">Expected Rent</td>
				<td style="width:5%;">-</td>
				<td style="width:15%; text-align:right;text-align: right;"><b>${data.amount}</b></td>
				<td style="width:10%;"></td>
			</tr>
			<tr height="30px">
				<td style="width:10%;"></td>
				<td style="width:15%; text-align: left;">Soild Units</td>
				<td style="width:5%;">-</td>
				<td style="width:15%;text-align: right;"><b>${data.sold_units}</b></td>
				<td style="width:5%;"></td>
				<td style="width:20%; text-align: left;"></td>
				<td style="width:5%;"></td>
				<td style="width:15%; text-align:right;text-align: right;"><b></b></td>
				<td style="width:10%;"></td>
			</tr>
		</table>
	</div><br>`
	frm.fields_dict.details_html.html(building_html);
}