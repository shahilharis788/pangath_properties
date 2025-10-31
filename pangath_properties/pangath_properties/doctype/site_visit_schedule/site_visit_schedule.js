// Copyright (c) 2024, iterative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Site Visit Schedule", {
    refresh(frm) {
          frm.add_custom_button(__("Visitor Feedback"), () => {
              frappe.model.open_mapped_doc({
                  method: "pangath_properties.pangath_properties.doctype.site_visit_schedule.site_visit_schedule.create_site_visit_feedback",
                  frm:frm
              })
        // frappe.new_doc('Visitor Feedback', {
        //   visitors__full_name: frm.doc.visitors_full_name,
              //     date_of_visit:frm.doc.date_of_visiting,
              //     unit:frm.doc.unit,
              //     property_name:frm.doc.property_name,
              //     property_address:frm.doc.property_address,
              //     email_id:frm.doc.email_id,
        //   phone:frm.doc.phone
        // });
      }, ("Create"));
      if (frm.doc.opportunity && frm.doc.__islocal) {
        let d = new frappe.ui.Dialog({
            title: 'Select Property And Unit',
            fields: [
                {
                    fieldname: 'property_units',
                    fieldtype: 'Table',
                    label: 'Property Units',
                    fields: [
                        {
                            fieldname: 'property',
                            fieldtype: 'Data',
                            label: 'Property',
                            in_list_view: 1
                        },
                        {
                            fieldname: 'unit',
                            fieldtype: 'Data',
                            label: 'Unit',
                            in_list_view: 1
                        },
                        {
                            fieldname: 'unit_no',
                            fieldtype: 'Data',
                            label: 'Unit No',
                            in_list_view: 1
                        },
                        {
                          fieldname: 'unit_type',
                          fieldtype: 'Data',
                          label: 'Unit Type',
                          in_list_view: 1
                        },
                        {
                          fieldname: 'yearly_rent',
                          fieldtype: 'Data',
                          label: 'Yearly Rent',
                          in_list_view: 1
                        },
                    ]
                }
            ],
            size: 'large', // small, large, extra-large 
            primary_action_label: 'Submit',
            primary_action(values) {
              if (values.property_units && values.property_units.length > 0){
                let selected_data  = d.fields_dict.property_units.grid.get_selected_children();
              if (selected_data.length == 1) {
                let details = selected_data.map(item => ({
                  property: item.property,
                  unit: item.unit,
                 
              }));
  
              
              if (details.length > 0) {
                  let first_item = details[0];
                  frm.set_value('property_id', first_item.property);
                  frm.set_value('unit', first_item.unit);
              }
                 
              }
              if(selected_data.length >1){
                  frappe.throw("Select Only One Row")
              }
            }
                d.hide();
            }
        });
    
        frappe.db.get_doc('Opportunity', frm.doc.opportunity).then(r => {
            if (r) {
                const property_units_data = r.custom_property_and_unit || [];
    
                // Clear existing rows and add new rows to the table
                d.fields_dict.property_units.grid.df.data = [];
                property_units_data.forEach(row => {
                    d.fields_dict.property_units.grid.df.data.push({
                        property: row.property,
                        unit: row.unit,
                        unit_no: row.unit_no,
                        unit_type:row.unit_type,
                        yearly_rent:row.yearly_rent
                    });
                });
    
                // Refresh the table grid
                d.fields_dict.property_units.grid.refresh();
            }
        }).catch(err => {
            console.error('Error fetching Opportunity:', err);
        });
    
        d.show();
    }
      }

  });
  