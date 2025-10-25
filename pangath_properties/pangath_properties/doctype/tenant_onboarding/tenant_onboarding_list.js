frappe.listview_settings["Tenant Onboarding"] = {
	get_indicator: function(doc) {
	  if (doc.status == "Terminated") {
		return [__("Terminated"), "grey", "status,=, Terminated"];
	  }
	  if (doc.status == "Expired") {
		return [__("Expired"), "orange", "status,=, Expired"];
	  }
	  if (doc.status == "Active" && doc.docstatus ==1) {
		return [__("Submitted"), "blue", "status,=, Submitted"];
	  }
	},
	before_render() {
		frappe.call({
		  method: 'real_estate.real_estate.doctype.tenant_onboarding.tenant_onboarding.change_status',
		  // callback: function(r) {
		  // }
		});
	  }
  
  };