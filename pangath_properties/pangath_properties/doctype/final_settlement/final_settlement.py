# Copyright (c) 2024, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class FinalSettlement(Document):

    def on_submit(doc):
        frappe.db.set_value("Tenancy Contract",doc.tenancy_contract,"new_renewal_lease","Closed")
        frappe.db.set_value("Unit",doc.unit,"status","Not Hand Over")

   

@frappe.whitelist()
def create_payment_entry(source_name, target_doc=None):
    if source_name:
        def set_missing_values(source, target):
            target.party_type = "Customer"        
        doclist = get_mapped_doc(
            "Final Settlement", 
            source_name, 
            {
                "Final Settlement": {
                    "doctype": "Payment Entry",
                    "field_map": {
                        "customer": "party",
                        "name": "custom_tenancy_application",
                        "customer_name": "party_name"
                    }
                }
            }, 
            target_doc, 
            set_missing_values
        )
        return doclist

