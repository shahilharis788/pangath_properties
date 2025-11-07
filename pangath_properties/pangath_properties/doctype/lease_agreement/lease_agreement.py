# Copyright (c) 2022, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class LeaseAgreement(Document):
	def validate(self):
		if self.is_existing_customer:
			pass
		else:
			error_log = []
			if not self.custom_emirates_id:
				error_log.append("Emirates Id")
			if not self.payment_terms_template:
				error_log.append("Payment Terms Template")
			if not self.tax_id:
				error_log.append("Tax Id")
			if error_log:
				error_log = ",".join(error_log)
				frappe.throw(f'Enter {error_log}')

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


@frappe.whitelist()
def create_customer(exist_cus, cust, passport_no, contact_no, email, nationality, emirates_id, territory, tax_id, payment_terms):
	
	if exist_cus == "1":
		return
	if frappe.db.exists("Customer", {"name": cust}):
			return
	
	customer = frappe.new_doc("Customer")
	customer.customer_name = cust
	customer.custom_passport_no = passport_no if passport_no else None
	customer.custom_contact_no = contact_no if contact_no else None
	customer.email_id = email if email else None
	customer.custom_nationality = nationality
	customer.custom_emirate_id = emirates_id
	customer.territory = territory if territory else None
	customer.tax_id = tax_id
	customer.payment_terms = payment_terms
	customer.save()
	return {"status": "created"}