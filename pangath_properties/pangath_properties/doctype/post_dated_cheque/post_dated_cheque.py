# Copyright (c) 2024, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class PostDatedCheque(Document):
	def on_update_after_submit(self):
		tenancy_contract = frappe.get_doc("TC Payment Schedule",self.reference)
		if tenancy_contract:
			tenancy_contract.db_set("date_of_issue",self.date_of_issue)
			tenancy_contract.db_set("expiry_date",self.expiry_date)
			tenancy_contract.db_set("cheque_date",self.cheque_date)
			tenancy_contract.db_set("cheque_number",self.cheque__no)
			tenancy_contract.db_set("cheque_status",self.status)
	pass

	def before_submit(self):
		np_doc = frappe.new_doc("Payment Entry")
		mop_list = frappe.get_list('Mode of Payment', pluck='name')

		mode_of_payment = ""
		# pdc_amount = 0
		contract = frappe.get_doc("Tenancy Contract", self.tenancy_contract)
		for row in contract.payment_schedule:
			if row.is_pdc == 1:
				mode_of_payment = row.mode_of_payment
				

		# if "PDC" not in mop_list:
		# 	frappe.throw("Mode of Payment 'PDC' does not exist.")

		np_doc.update({
			'payment_type': "Receive",  # or "Pay", depending on context
			'mode_of_payment': mode_of_payment,
			'party_type': self.party_type,
			# 'custom_status_field':'Uncleared',
			'party': self.party,
			'party_name': self.party,
			'posting_date': frappe.utils.nowdate(),
			'paid_amount': self.cheque_amount,
			'cost_center': frappe.db.get_value("Company", self.company, "cost_center"),
			'received_amount': self.cheque_amount,
			"reference_date": self.cheque_date,  
			"reference_no": self.name,
			'paid_to': frappe.db.get_value("Mode of Payment Account", {
				"parent": mode_of_payment,
				"company": self.company
			}, "custom__bank_clearance_account")
		})

		np_doc.append('references', {
			'reference_doctype': 'Sales Invoice',
			'reference_name': self.sales_invoice,
			'allocated_amount': self.cheque_amount
		})

		np_doc.insert()
		np_doc.submit()
		frappe.db.commit()
		frappe.db.set_value("Payment Entry", np_doc.name, "custom_status_field", "Uncleared")
		
@frappe.whitelist()
def cheque_status(name,status):
	date = nowdate()
	doc = frappe.get_doc("Post Dated Cheque", name)
	
	# Check if any child row in cheque_audit_trail already has status 'Cleared'
	if any(child.status == "Cleared" for child in doc.get("cheque_audit_trail", [])):
		frappe.throw("This cheque is already cleared.")

	if not doc.bank_account:
		frappe.throw("Bank Account is not set for this cheque.")
	doc.append(
		"cheque_audit_trail",
		{
			"transaction_date": date,
			"status": status,
			"previous__status": doc.status,
			"reference": doc.cheque__no,
			"remarks": f"Cheque status changed from {doc.status} To {status}"
		},
	)
	doc.status = status
	doc.save()
	doc.submit()
	create_journal_entry(doc)


def create_journal_entry(pdc_doc):
	doc = frappe.get_doc('Payment Entry', {'reference_no': pdc_doc.name, 'docstatus':1},'name')
	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry" 
	je.posting_date = nowdate()
	je.company = pdc_doc.company

	je.user_remark = f"Auto JV for cleared PDC {pdc_doc.name}"
	
	je.append("accounts", {
		"account": doc.paid_to,
		"credit_in_account_currency": doc.paid_amount,
	})

	je.append("accounts", {
		"account": pdc_doc.bank_account,  
		"debit_in_account_currency": pdc_doc.cheque_amount
	})

	je.insert()
	je.submit()

	frappe.msgprint(f'Journal Entry <a href="/app/journal-entry/{je.name}" target="_blank">{je.name}</a> created and submitted.', indicator='green')
