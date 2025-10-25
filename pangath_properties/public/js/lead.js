frappe.ui.form.on("Lead", {
    onload: function(frm) {
        set_unit_query(frm);
    },

    custom_property: function(frm) { 
        frm.set_value("custom_unit", null);
        set_unit_query(frm);
    }
});

function set_unit_query(frm) {
    if (frm.doc.custom_property) {  
        frm.set_query("custom_unit", function() {
            return {
                filters: {
                    property: frm.doc.custom_property,  
                    status: ["!=", "Rented"]
                }
            };
        });
    } else {
       
        frm.set_query("custom_unit", function() {
            return {
                filters: {
                    name: ["is", "not set"]
                }
            };
        });
    }
}