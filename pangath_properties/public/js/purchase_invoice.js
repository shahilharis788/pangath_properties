frappe.ui.form.on("Purchase Invoice", {
    refresh: function (frm) {
        setTimeout(() => {
            frm.set_query('customer', function (doc) {
                return { "filters": [] };
            });
        }, 2000);

        frm.add_custom_button('Insert Records', function () {
            let d = new frappe.ui.Dialog({
                title: 'Insert Records',
                fields: [
                    {
                        label: 'Items Table',
                        fieldname: 'items_table',
                        fieldtype: 'Table',
                        in_place_edit: true,
                        fields: [
                            {
                                fieldtype: 'Link',
                                label: 'Item Code',
                                fieldname: 'item_code',
                                options: 'Item',
                                reqd: 1,
                                in_list_view: 1,
                                columns: 2
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
                                columns: 1,
                                read_only_depends_on: 'eval:doc.entry_for=="Property"'
                            },
                            {
                                fieldtype: 'Link',
                                label: 'Property',
                                fieldname: 'property',
                                options: 'Property',
                                in_list_view: 1,
                                columns: 2,
                                read_only_depends_on: 'eval:doc.entry_for=="Unit"'
                            },
                            {
                                fieldtype: 'Float',
                                label: 'Qty',
                                fieldname: 'qty',
                                columns: 1,
                                default: 1
                            },
                            {
                                fieldtype: 'Currency',
                                label: 'Rate',
                                fieldname: 'rate',
                                in_list_view: 1,
                                columns: 2
                            }
                        ]
                    }
                ],

                primary_action(values) {
                    frm.clear_table('items');
                    frappe.call({
                        method: 'pangath_properties.events.purchase_invoice.get_units_property_items',
                        args: {
                            data: values.items_table
                        },
                        callback: function (r) {
                            if (r.message) {
                                r.message.forEach(row => {
                                    frm.add_child('items', {
                                        item_code: row.item_code,
                                        qty: 1,
                                        item_name: row.item_name,
                                        uom: row.uom,
                                        rate: row.qty * row.rate,
                                        amount: row.qty * row.rate,
                                        property: row.property,
                                        unit: row.unit
                                    });
                                });
                                frm.refresh_field('items');
                            }
                        }
                    });
                    d.hide();
                }
            });

            d.show();
        });
    }
});
