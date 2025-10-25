# Copyright (c) 2024, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class ConditionInspection(Document):
    def validate(self):
        total = 0
        for i in self.reading:
            total += flt(i.amount)
        self.total_amount = total
    pass


    
    
@frappe.whitelist()
def create_move_out(source_name, target_doc=None):
    if source_name:
        def set_missing_values(source, target):
            target.run_method("set_missing_values")
        doclist = get_mapped_doc("Condition Inspection", source_name, {
            "Condition Inspection": {
                "doctype": "Condition Inspection"
            },
         

        }, target_doc, set_missing_values)
        doclist.inspection_type = "Move-Out"
        return doclist




@frappe.whitelist()
def final_settlement(source_name, target_doc=None):
    if source_name:
        ci = frappe.get_doc("Condition Inspection",source_name)
        tc = frappe.get_doc("Tenancy Contract",ci.tenancy_contract)
        s = 0
        for i in tc.type_of_charges:
            if i.refund == "Yes":
                s += i.amount

        penalty = 0
        for i in ci.reading:
            penalty += i.amount
        
        refund = s - penalty
        def set_missing_values(source, target):
            target.run_method("set_missing_values")
        doclist = get_mapped_doc("Condition Inspection", source_name, {
            "Condition Inspection": {
                "doctype": "Final Settlement"
            },
         

        }, target_doc, set_missing_values)
        doclist.security_deposit = s
        doclist.penalty = penalty
        doclist.refundable_amount = refund
        return doclist

