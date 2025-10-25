# Copyright (c) 2025, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from typing import Literal

import frappe
import frappe.utils
from frappe import _, qb
from frappe.contacts.doctype.address.address import get_company_address
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.party import get_party_account
from erpnext.controllers.selling_controller import SellingController
from erpnext.manufacturing.doctype.blanket_order.blanket_order import (
	validate_against_blanket_order,
)
from erpnext.manufacturing.doctype.production_plan.production_plan import (
	get_items_for_material_requests,
)
from erpnext.selling.doctype.customer.customer import check_credit_limit
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
	get_sre_reserved_qty_details_for_voucher,
	has_reserved_stock,
)
from erpnext.stock.get_item_details import get_bin_details, get_default_bom, get_price_list_rate
from erpnext.stock.stock_balance import get_reserved_qty, update_bin_qty

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}

class ProformaInvoice(Document):
	pass

@frappe.whitelist()
def make_sales_invoice_from_proforma(source_name, target_doc=None, ignore_permissions=False):
    proforma_doc = frappe.get_doc("Proforma Invoice", source_name)

    def postprocess(source, target):
        set_missing_values(source, target)
        if target.get("allocate_advances_automatically"):
            target.set_advances()

    def set_missing_values(source, target):
        target.flags.ignore_permissions = True
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")
        target.run_method("set_use_serial_batch_fields")

        if source.company_address:
            target.update({"company_address": source.company_address})
        else:
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

        if source.loyalty_points and source.order_type == "Shopping Cart":
            target.redeem_loyalty_points = 1

        target.debit_to = get_party_account("Customer", source.customer, source.company)

    def update_item(source_doc, target_doc, source_parent):
        # Find qty from Proforma Invoice Details based on item_code
        target_doc.custom_proforma_invoice = proforma_doc.name
        matching_item = next(
            (item for item in proforma_doc.item_details if item.item_code == source_doc.item_code),
            None
        )
        if matching_item:
            target_doc.qty = matching_item.qty
        else:
            target_doc.qty = 0  # fallback if not found

        target_doc.amount = flt(source_doc.amount) - flt(source_doc.billed_amt)
        target_doc.base_amount = target_doc.amount * flt(source_parent.conversion_rate)

        if source_parent.project:
            target_doc.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center")

        if target_doc.item_code:
            item = get_item_defaults(target_doc.item_code, source_parent.company)
            item_group = get_item_group_defaults(target_doc.item_code, source_parent.company)
            cost_center = item.get("selling_cost_center") or item_group.get("selling_cost_center")
            if cost_center:
                target_doc.cost_center = cost_center

    doclist = get_mapped_doc(
        "Sales Order",
        proforma_doc.sales_order,  # This is the actual Sales Order
        {
            "Sales Order": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "party_account_currency": "party_account_currency",
                    "payment_terms_template": "payment_terms_template",
                },
                "field_no_map": ["payment_terms_template"],
                "validation": {"docstatus": ["=", 1]},
            },
            "Sales Order Item": {
                "doctype": "Sales Invoice Item",
                "field_map": {
                    "name": "so_detail",
                    "parent": "sales_order",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.qty
                    and (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "reset_value": True,
            },
            "Sales Team": {
                "doctype": "Sales Team",
                "add_if_empty": True,
            },
        },
        target_doc,
        postprocess,
        ignore_permissions=ignore_permissions,
    )

    if cint(frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")):
        doclist.set_payment_schedule()

    return doclist
