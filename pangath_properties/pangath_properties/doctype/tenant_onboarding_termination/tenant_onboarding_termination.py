# Copyright (c) 2023, iterative and contributors
# For license information, please see license.txt

import erpnext
import frappe
from frappe.model.document import Document
from erpnext.accounts.party import get_party_account
from frappe import _
from frappe.utils.data import getdate,date_diff,rounded
from erpnext.setup.utils import get_exchange_rate
from frappe.utils import flt

class TenantOnboardingTermination(Document):
	def on_submit(self):
		cost_center = frappe.db.get_value("Company",self.company,"cost_center")
		if not cost_center:
			frappe.throw(f"Configure Default Cost Center for company {frappe.bold(self.company)}")

		to_doc = frappe.get_doc('Tenant Onboarding', self.tenant_onboarding)

		if self.rental_income:
			for i in self.rental_income:
				journal_entry_doc = frappe.new_doc('Journal Entry')
				journal_entry_doc.company = self.company
				journal_entry_doc.posting_date = frappe.utils.nowdate()
				journal_entry_doc.tenant_onboarding_termination = self.name
				journal_entry_doc.append("accounts", {
					'account': frappe.db.get_value('Company', {"name":self.company}, 'default_rental_income'),
					'credit_in_account_currency': i.rent,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.append("accounts", {
					'account': frappe.db.get_value('Tenant Onboarding', self.tenant_onboarding, 'deferred_revenue_account'),
					'debit_in_account_currency':  i.rent,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.submit()
				frappe.db.set_value(i.doctype, i.name, 'journal_entry_created', 1)
				frappe.db.set_value(i.doctype, i.name, 'journal_entry', journal_entry_doc.name)

		if self.reverse_deferred_revenue:
			for k in self.reverse_deferred_revenue:
				journal_entry_doc = frappe.new_doc('Journal Entry')
				journal_entry_doc.company = self.company
				journal_entry_doc.posting_date = self.posting_date
				journal_entry_doc.tenant_onboarding_termination = self.name
				journal_entry_doc.append("accounts", {
					'account': to_doc.deferred_revenue_account,
					'debit_in_account_currency': k.rent,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.append("accounts", {
					'party_type': "Customer",
					'party': self.customer,
					'account':frappe.db.get_value('Party Account',{'parent' : self.customer, 'company': self.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : self.customer, 'company': self.company}, 'account') else frappe.db.get_value('Company', self.company, 'default_receivable_account'),
					'credit_in_account_currency': k.rent,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.submit()
				k.journal_entry_created = 1
				frappe.db.set_value(k.doctype, k.name, {
					'journal_entry_created': 1,
					'journal_entry': journal_entry_doc.name
				})

		for j in to_doc.deferred_revenue_schedule:
			if j.start_date <= getdate(self.termination_date) <= j.end_date:
				frappe.db.set_value(j.doctype, j.name, 'terminated', 1)
			elif getdate(self.termination_date) < j.end_date:
				frappe.db.set_value(j.doctype, j.name, 'terminated', 1)

		#Type of Charges Reversal for refunds
		for m in to_doc.type_of_charges:
			if m.refund == 'Yes' and m.payment_entry_created == 1 and m.status != "Cleared":
				journal_entry_doc = frappe.new_doc('Journal Entry')
				journal_entry_doc.company = to_doc.company
				# journal_entry_doc.posting_date = to_doc.posting_date
				journal_entry_doc.posting_date = self.termination_date
				journal_entry_doc.tenant_onboarding_termination = self.name
				journal_entry_doc.append("accounts", {
					'account': m.account,
					'debit_in_account_currency': m.amount,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.append("accounts", {
					'party_type': "Customer",
					'party': to_doc.customer,
					# 'account': frappe.db.get_value('Party Account',{'parent' : to_doc.customer, 'company': to_doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : to_doc.customer, 'company': to_doc.company}, 'account') else frappe.db.get_value('Company', self.company, 'default_receivable_account'),
					'account':frappe.db.get_value("Mode of Payment Account", {"parent":m.mode_of_payment, "company":self.company},"default_account"),
					'credit_in_account_currency':  m.amount,
					'cost_center' : cost_center,
					'unit':self.unit,
					'customer':self.customer,
					'property':self.property
				})
				journal_entry_doc.submit()

		#Penality And Other Expenses
		if self.penality_and_other_expenses:
			for penality in self.penality_and_other_expenses:
				if penality.journal_entry_created == 0:
					journal_entry_doc = frappe.new_doc('Journal Entry')
					journal_entry_doc.company = to_doc.company
					journal_entry_doc.posting_date = self.termination_date
					journal_entry_doc.tenant_onboarding_termination = self.name
					journal_entry_doc.append("accounts", {
						'account': penality.account,
						'credit_in_account_currency': penality.amount,
						'cost_center' : cost_center,
						'unit':self.unit,
						'customer':self.customer,
						'property':self.property
					})
					journal_entry_doc.append("accounts", {
						'party_type': "Customer",
						'party': to_doc.customer,
						'account':frappe.db.get_value('Company', self.company, 'default_receivable_account'),
						'debit_in_account_currency':  penality.amount,
						'cost_center' : cost_center,
						'unit':self.unit,
						'customer':self.customer,
						'property':self.property
					})
					journal_entry_doc.submit()
					frappe.db.set_value(penality.doctype, penality.name, 'journal_entry_created', 1)
					frappe.db.set_value(penality.doctype, penality.name, 'journal_entry', journal_entry_doc.name)

		frappe.db.set_value('Tenant Onboarding', self.tenant_onboarding, 'status', 'Terminated')
		frappe.db.set_value("Unit",self.unit,'status',"Available")

	def validate(self):
		if not self.default_currency:
			self.default_currency = erpnext.get_company_currency(self.company)

		if self.penality_and_other_expenses:
			amount = 0
			for k in self.penality_and_other_expenses:
				amount = amount + k.amount
			self.penality = amount
		else:
			self.penality = 0
		pdc=0
		cleared=0
		if self.payment_schedule:
			for i in self.payment_schedule:
				if i.status == "Return Cheque":
					pdc+=i.payment_amount
				if i.status == "Cleared":
					cleared+=i.payment_amount
		to=frappe.get_doc("Tenant Onboarding",self.tenant_onboarding)
		clr_depo=0
		pdc_depo=0
		for i in to.type_of_charges:
			if i.refund == 'Yes':
				if i.status == "Cleared":
					clr_depo=clr_depo+i.amount
				if  i.status == "PDC Created":
					pdc_depo=pdc_depo+i.amount

		cleared_refundable= flt(cleared)-flt(self.occupied_rent)
		self.refund_cleared=rounded(cleared_refundable,2)
		self.refund_pdc=pdc+pdc_depo
		total_refundable=clr_depo+self.refund_cleared-self.penality
		self.total_refundable=total_refundable
		if getdate(self.termination_date) < getdate(self.period_start_date )or getdate(self.termination_date) > getdate(self.period_end_date):
			frappe.throw("Termination date should be between period start date and period end date")


	def on_cancel(self):
		if self.rental_income:
			for i in self.rental_income:
				frappe.db.set_value(i.doctype, i.name, 'journal_entry_created', 0)
				frappe.db.set_value(i.doctype, i.name, 'journal_entry', '')

		if self.penality_and_other_expenses:
			for i in self.penality_and_other_expenses:
				frappe.db.set_value(i.doctype, i.name, 'journal_entry_created', 0)
				frappe.db.set_value(i.doctype, i.name, 'journal_entry', '')

	def on_trash(self):
		if frappe.db.exists("Tenant Onboarding",{"name":self.tenant_onboarding,"docstatus":1}):
			doc = frappe.get_doc("Tenant Onboarding",{"name":self.tenant_onboarding,"docstatus":1})
			doc.status="Active"
			doc.submit()
		


@frappe.whitelist()
def create_payment_entry(doc):
	import json
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe._dict(doc)
	default_currency = doc.default_currency if doc.default_currency else erpnext.get_company_currency(doc.company)
	pe = frappe.new_doc('Payment Entry')
	pe.voucher_type = 'Payment Entry'
	pe.company = doc.company
	pe.posting_date = getdate()
	pe.payment_type = "Pay"
	pe.party_type = "Customer"
	pe.party = doc.customer
	pe.paid_to = get_party_account("Customer", doc.customer, pe.company)
	pe.paid_amount= doc.total_refundable
	pe.received_amount = doc.total_refundable
	pe.tenant_onboarding = doc.tenant_onboarding
	pe.tenant_onboarding_termination = doc.name
	pe.customer = doc.customer
	pe.unit = doc.unit
	pe.total_allocated_amount = doc.total_refundable
	pe.source_exchange_rate = get_exchange_rate(default_currency, erpnext.get_company_currency(doc.company), doc.termination_date)
	pe.custom_remarks = True
	pe.setup_party_account_field()
	pe.set_missing_values()
	pe.set_missing_ref_details()
	pe.append("references",{
		"reference_doctype" : "Tenant Onboarding Termination",
		"reference_name": doc.name,
		"total_amount" : doc.total_refundable,
		"outstanding_amount" : doc.total_refundable,
		"allocated_amount" : doc.total_refundable
	})

	pe.insert(ignore_permissions=True, ignore_mandatory=True)
	return pe.name