import frappe
from frappe.model.mapper import get_mapped_doc



@frappe.whitelist()
def make_proforma_invoice(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.flags.ignore_permissions = True
        # Additional logic if needed

    def update_item(source_doc, target_doc, source_parent):
        # Calculate already invoiced quantity for this item in submitted Sales Invoices
        invoiced_qty = frappe.db.sql("""
            SELECT SUM(sii.qty)
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE sii.sales_order = %s
              AND sii.item_code = %s
              AND si.docstatus = 1
        """, (source_doc.parent, source_doc.item_code))[0][0] or 0

        remaining_qty = source_doc.qty - invoiced_qty

        if remaining_qty > 0:
            target_doc.qty = remaining_qty
            target_doc.amount = remaining_qty * source_doc.rate
        else:
            # prevent mapping if no quantity left to invoice
            target_doc.qty = 0
            target_doc.amount = 0

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Proforma Invoice",
                "field_map": {
                    "customer": "customer",
                    "customer_name": "customer_name",
                    "transaction_date": "posting_date",
                    "company": "company",
                    "currency": "currency",
                    "selling_price_list": "selling_price_list",
                    "price_list_currency": "price_list_currency",
                    "plc_conversion_rate": "plc_conversion_rate",
                    "conversion_rate": "conversion_rate",
                    "project": "project",
                    "order_type": "order_type",
                    "po_no": "po_no",
                    "po_date": "po_date",
                    "delivery_date": "delivery_date",
                    "sales_order": "name"
                },
                "validation": {
                    "docstatus": ["=", 1]
                }
            },
            "Sales Order Item": {
                "doctype": "Proforma Invoice details",
                "field_map": {
                    "item_code": "item_code",
                    "item_name": "item_name",
                    "description": "description",
                    "uom": "uom",
                    "rate": "rate",
                    "warehouse": "warehouse",
                    "delivery_date": "delivery_date",
                    "name": "sales_order_item"
                },
                "postprocess": update_item
            }
        },
        target_doc,
        set_missing_values
    )

    # Remove items with zero qty

    return doc

