frappe.pages['building_view'].on_page_load = function(wrapper) {
	new Building(wrapper);
}

Building = Class.extend({
	init: function(parent) {
		this.parent = parent;
		this.make_page();
		this.get_building_details();
	},
	make_page: function() {
		if (this.page)
			return;

		frappe.ui.make_app_page({
			parent: this.parent,
			title: __('Building View'),
			single_column: true
		});
		this.page = this.parent.page;
		this.wrapper = $('<div></div>').appendTo(this.page.main);
	},
	get_building_details: function() {
		var me = this;
		me.wrapper.empty();
		return frappe.call({
			method: "real_estate.real_estate.page.building_view.building_view.get_buildings",
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
			freeze_message: 'Loading Building View'
		});
	},
	make_list: function (buildings) {
		var me = this;
		$(`<div id="products-grid-area" class="row products-list mt-minus-1">`).appendTo(me.wrapper)
		$.each(buildings, function(i, building){
			$(frappe.render_template("building_view", {data:building})).appendTo(me.wrapper);
		});
		$(`</div>`).appendTo(me.wrapper)

	},

})