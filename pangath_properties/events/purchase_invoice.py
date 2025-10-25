import frappe

def after_insert_purchase_invoice(doc, method):
    if doc.inter_company_invoice_reference:
        sales_invoice_name = doc.inter_company_invoice_reference
        sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
        sales_invoice.custom_inter_company_purchase_invoice_reference = doc.name
        sales_invoice.save(ignore_permissions=True)


@frappe.whitelist()
def get_units_property_items(data):
    data = frappe.parse_json(data)
    result = []

    for row in data:
        qty = row.get('qty') or 0
        rate = row.get('rate') or 0
        entry_for = row.get('entry_for')

        if row.get("item_code"):
            item = frappe.db.get_value(
                "Item", row.get("item_code"),
                ["item_name", "stock_uom"],
                as_dict=True
            )
        else:
            item = {"item_name": None, "stock_uom": None}

        if entry_for == 'Property':
            unit_list = frappe.db.get_list(
                'Unit',
                filters={'property': row.get('property')},
                fields=['name', 'property']
            )
            num_units = len(unit_list)
            per_qty = qty / num_units if num_units else qty

            if num_units > 0:
                for unit in unit_list:
                    entry = row.copy()
                    entry['property'] = unit.get('property')
                    entry['unit'] = unit.get('name')
                    entry['qty'] = per_qty
                    entry['amount'] = per_qty * rate
                    entry['item_name'] = item.get("item_name")
                    entry['uom'] = item.get("stock_uom")
                    result.append(entry)
            else:
                row['item_name'] = item.get("item_name")
                row['uom'] = item.get("stock_uom")
                result.append(row)

        elif entry_for == 'Unit':
            list_unit = frappe.db.get_list(
                'Unit',
                filters={'is_group': 0, 'parent_unit': row.get('unit')},
                fields=['name']
            )
            num_units = len(list_unit)
            per_qty = qty / num_units if num_units else qty

            if num_units > 0:
                for unit in list_unit:
                    entry = row.copy()
                    entry['unit'] = unit.get('name')
                    entry['qty'] = per_qty
                    entry['amount'] = per_qty * rate
                    entry['item_name'] = item.get("item_name")
                    entry['uom'] = item.get("stock_uom")
                    result.append(entry)
            else:
                row['item_name'] = item.get("item_name")
                row['uom'] = item.get("stock_uom")
                result.append(row)

        else:
            row['item_name'] = item.get("item_name")
            row['uom'] = item.get("stock_uom")
            result.append(row)

    return result

