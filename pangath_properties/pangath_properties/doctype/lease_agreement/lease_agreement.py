# Copyright (c) 2022, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeaseAgreement(Document):
    pass
	# def on_submit(self):
	# 	la_doc = frappe.get_doc("Tenant Onboarding",self.lease_application)
	# 	for i in la_doc.payment_schedule:
	# 		if i.status != "PDC Created" and i.mode_of_payment == "Cheque":
	# 			pdc = frappe.get_doc(
	# 				{
	# 					"doctype": "Post Dated Cheque",
	# 					"customer" : la_doc.customer,
	# 					"unit" : la_doc.unit,
	# 					"building": la_doc.building,
	# 					"posting_date": i.payment_scheduled_date,
	# 					"cheque_reference_number": i.payment_scheduled_date,
	# 					"cheque_reference_date" :i.reference_date,
	# 					"lease_application" : la_doc.name,
	# 					"lease_application_child" : i.name,
	# 					"lease_agreement": self.name
	# 				}
	# 			).insert(ignore_permissions=True, ignore_mandatory=True)
	# 			if pdc.name:
	# 				frappe.db.set_value("LA Repayment Schedule", i.name, "status", "PDC Created")