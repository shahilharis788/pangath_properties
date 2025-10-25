# Copyright (c) 2023, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint,flt
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


class Unit(NestedSet):
	nsm_parent_field = "parent_unit"

	def on_update(self):
		self.update_nsm_model()

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def on_trash(self):
		self.update_nsm_model()

	def after_insert(self):
		self.unit_no=self.name
		self.id=self.name
		self.unit_name=self.name

		if frappe.db.exists('Item', self.name):
			self.item = self.name
		else:
			new_item = frappe.get_doc({
				'doctype': 'Item',
				'item_code': self.name,
				'item_name': self.name,
				'item_group': 'All Item Groups',
				'description': self.name,
				'stock_uom': 'Nos',
				'is_sales_item': 1,
				'show_in_website': 0,
				'is_pro_applicable': 0,
				'disabled': 0
			}).insert(ignore_permissions=True)
			self.item = new_item.item_code
		self.save()

	def validate(self):
		if self.rent:
			monthly_rent=round(self.rent/12)
			self.monthly_rent=monthly_rent

		k = 0
		if self.owner_details:
			for i in self.owner_details:
				k = flt(k) + flt(i.ownership_)
			if k < 100:
				frappe.msgprint('Ownership percentage cannot be less than 100 in Owner details section')
			elif k > 100:
				frappe.msgprint('Ownership percentage cannot be more than 100 in Owner details section')


	def before_rename(self,doc, old, new):
		pass

	def after_rename(self,doc, old, new):
		self.id=self.name
		self.unit_name=self.name
		self.unit_no= self.name
		self.save()


@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args

	args = make_tree_args(**frappe.form_dict)

	if cint(args.is_root):
		args.parent_unit = None

	frappe.get_doc(args).insert()


@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
	if is_root:
		parent = ""

	fields = ["name as value", "is_group as expandable"]
	filters = [
		["ifnull(`parent_unit`, '')", "=", parent],
		["company", "in", (company, None, "")],
	]

	return frappe.get_list(doctype, fields=fields, filters=filters, order_by="name")

@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
    if is_root:
        parent = ""

    filters = {"parent_unit": parent}
    if company:
        filters["company"] = company

    units = frappe.get_all(
        "Unit",
        fields=["name", "unit_no", "status", "is_group"],
        filters=filters,
        order_by="unit_no"
    )

    children = []

    for d in units:
        if d.is_group:
            # Aggregate all descendant units (using nested set lft/rgt if Unit is a tree doctype)
            totals = frappe.db.sql("""
                SELECT
                    IFNULL(SUM(gl.debit), 0) AS total_debit,
                    IFNULL(SUM(gl.credit), 0) AS total_credit
                FROM `tabGL Entry` gl
                LEFT JOIN `tabAccount` ac ON ac.name = gl.account
                WHERE gl.unit IN (
                    SELECT name FROM `tabUnit`
                    WHERE lft >= (SELECT lft FROM `tabUnit` WHERE name=%s)
                      AND rgt <= (SELECT rgt FROM `tabUnit` WHERE name=%s)
                )
                AND ac.root_type IN ('Expense', 'Income');
            """, (d.name, d.name), as_dict=1)[0]
        else:
            # Only this unit
            totals = frappe.db.sql("""
                SELECT
                    IFNULL(SUM(gl.debit), 0) AS total_debit,
                    IFNULL(SUM(gl.credit), 0) AS total_credit
                FROM `tabGL Entry` gl
                LEFT JOIN `tabAccount` ac ON ac.name = gl.account
                WHERE gl.unit = %s
                AND ac.root_type IN ('Expense', 'Income');
            """, (d.name,), as_dict=1)[0]

        debit = totals.total_debit or 0
        credit = totals.total_credit or 0
        balance = debit - credit

        children.append({
            "value": d.name,
            "unit_no": d.unit_no,
            "status": d.status,
            "credit": float(credit),
            "debit": float(debit),
            "balance": float(balance),
            "expandable": d.is_group
        })

    return children