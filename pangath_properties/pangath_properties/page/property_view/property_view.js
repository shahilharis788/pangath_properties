// frappe.pages['property-view'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'None',
// 		single_column: true
// 	});
// }

frappe.pages['property-view'].on_page_load = function(wrapper) {
	new Property(wrapper);
}

Property = Class.extend({
	init: function(parent) {
		this.parent = parent;
		this.make_page();
		this.get_property_details();
	},
	make_page: function() {
		if (this.page)
			return;

		frappe.ui.make_app_page({
			parent: this.parent,
			title: __('Property View'),
			single_column: true
		});
		this.page = this.parent.page;
		this.wrapper = $('<div></div>').appendTo(this.page.main);
	},
	get_property_details: function() {
		var me = this;
		me.wrapper.empty();
		return frappe.call({
			method: "real_estate.real_estate.page.property_view.property_view.get_properties",
			args: {
			},
			callback: function (r) {
				me.wrapper.empty();
				if(r.message.length > 0){
					me.make_list(r.message)
				}else{
					let msg_html = '<p class="text-muted" style="padding: 15px;">No '+ me.status.get_value() +' appointments  found for the day</p>';
					$(msg_html).appendTo(me.wrapper);
				}
			},
			freeze: true,
			freeze_message: 'Loading Property View'
		});
	},
	make_list: function (properties) {

		var me = this;
		$(`<div id="products-grid-area" class="row products-list mt-minus-1">`).appendTo(me.wrapper)
		$.each(properties, function(i, property){
			$(frappe.render_template("property_view", {data:property})).appendTo(me.wrapper);
		});
		$(`</div>`).appendTo(me.wrapper)

	},

})