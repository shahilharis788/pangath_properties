// Copyright (c) 2024, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Condition Inspection", {
    refresh:function(frm){
        if(frm.doc.docstatus == 1 && frm.doc.inspection_type == "Move-In"){
            frm.add_custom_button(__("Move-Out"), () => {
                frappe.model.open_mapped_doc({
                    method: "real_estate.real_estate.doctype.condition_inspection.condition_inspection.create_move_out",
                    frm:frm
                })
                
            });
        }
        if(frm.doc.docstatus == 1 && frm.doc.inspection_type == "Move-Out"){
            frm.add_custom_button(__("Final Settlement"), () => {
                frappe.model.open_mapped_doc({
                    method: "real_estate.real_estate.doctype.condition_inspection.condition_inspection.final_settlement",
                    frm:frm
                })
                
            });
        }
    },
    tenancy_contract:function(frm){
        if(frm.doc.tenancy_contract){
            frappe.db.get_doc("Tenancy Contract",frm.doc.tenancy_contract).then(r => {
                if(r.condition_inspection){
                    frm.clear_table('reading');
                    $.each(r.condition_inspection,function(i,d){
                        var row =frm.add_child("reading")
                        row.parameter = d.parameter
                        row.comment = d.comment
                        row.code = d.code
                        row.parameter_group =d.parameter_group
                    })
                    frm.refresh_field('reading');
                }
                
            })
        }
        else{
            frm.clear_table('reading');
            frm.refresh_field('reading');
        }
    },
    condition_inspection_template: function(frm) {
            if (frm.doc.condition_inspection_template) {
                frappe.db.get_doc("Condition Inspection Template",frm.doc.condition_inspection_template).then(r =>{
                    $.each(r.condition_inspection_parameter,function(i,d){
                        var row =frm.add_child("reading")
                        row.parameter = d.parameter
                        row.comment = d.comment
                        row.code = d.code
                        row.parameter_group =d.parameter_group
                    })
                    frm.refresh_field('reading');
                })
            }
            else{
                frm.clear_table('reading');
                frm.refresh_field('reading');
            }
        }
});
