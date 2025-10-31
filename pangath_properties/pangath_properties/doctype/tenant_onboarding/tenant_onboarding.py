# Copyright (c) 2022, iterative and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import (
    get_link_to_form,
	getdate,get_last_day,
	date_diff, get_first_day,
	add_to_date, nowdate,rounded
)

from erpnext.setup.utils import get_exchange_rate
from frappe.utils import flt

class TenantOnboarding(Document):
	def before_insert(self):
		if self.building and not self.tenancy_application:
			unit_list = frappe.db.get_all("Unit",{"property":self.building,"status":"Available"},pluck = "name")
			if unit_list:
				if not self.unit in unit_list:
					frappe.throw(f"{self.unit} is not available in {self.building}")

	def before_save(self):
		if self.payment_amount:
			self.monthly_rent = self.payment_amount / 12

		if not self.payment_schedule:
			populate_payment_schedule(self)
		if not self.deferred_revenue_schedule:
			populate_deferred_revenue_schedule(self)

		k=0
		j = 0
		if self.payment_schedule:
			for i in self.payment_schedule:
				k = k + i.payment_amount
		for o in self.type_of_charges:
			j = j + o.amount
		self.total = k +j

		if self.payment_amount:
			self.montly_rent = self.payment_amount / 12

		if self.posting_date and self.period_start_date:
			if self.posting_date > self.period_start_date:
				frappe.msgprint(msg='Posting Date should be less than or equal to period start date',)
		if self.payment_schedule:
			reference_number =[]
			for schedule in self.payment_schedule:
					reference_number.append(schedule.reference_number)
			if self.type_of_charges:
				for toc in self.type_of_charges:
					reference_number.append(toc.reference_number)
		
			for sch in self.payment_schedule:
				if sch.reference_number:
					if reference_number.count(sch.reference_number) > 1:
						frappe.msgprint(_("Reference number {1} is repeating in row {0} of Schedule Table").format(sch.idx,sch.reference_number))
						break
			for toch in self.type_of_charges:
				if toch.reference_number:
					if reference_number.count(toch.reference_number) > 1:
						frappe.msgprint(_("Reference number {1} is repeating in row {0} of Particulars Table").format(toch.idx,toch.reference_number))
						break


	def validate(self):
		if self.tenancy_application:
			tenancy_application_unit = frappe.db.get_value("Tenancy Application",self.tenancy_application,"unit")
			if tenancy_application_unit and tenancy_application_unit != self.unit:
				frappe.throw(f"Onboarding Unit is not matching with the Application Unit")

		if not self.period_start_date:
			frappe.throw(_("Period Start Date is mandatory"))
		end_num = self.number
		if self.number and self.period:
			if self.period == 'Year':
				end_num = self.number * 12
				days = self.number * 365
				self.period_end_date =  frappe.utils.add_days(frappe.utils.add_months(self.period_start_date, end_num),-1)
			elif self.period=='Month':
				self.period_end_date = frappe.utils.add_days(frappe.utils.add_months(self.period_start_date, end_num),-1)

	def on_submit(self):
		create_toc_payment_entry(self)
		if self.unit:
			frappe.db.set_value('Unit',self.unit,"status","Booked")
		if self.payment_schedule:
			for i in self.payment_schedule:
				if i.status == '':
					frappe.throw("Status is mandatory in Payment Schedule")
				if not i.status =="Unpaid" and not i.reference_date:
					frappe.throw("Reference Date is Mandatory")
		if self.type_of_charges:
			for i in self.type_of_charges:
				if not i.status:
					frappe.throw("Status is Mandatory")
				if not i.reference_number:
					frappe.throw("Reference Number is Mandartory")
				if not i.reference_date:
					frappe.throw("Reference Date is Mandatory")
		self.reload()

	def on_update_after_submit(self):
		for schedule in  self.payment_schedule:
			if schedule.status == 'Return Cheque':
				je_doc = frappe.get_doc('Journal Entry', schedule.journal_entry)
				if je_doc.payment_entry:
					pe_doc = frappe.get_doc('Payment Entry', je_doc.payment_entry)
					pe_doc.db_set("status_je", schedule.status)
					pe_doc.cancel()
				je_doc.db_set("payment_entry", '')
				je_doc.db_set("pe_created", 0)
				je_doc.db_set("status", schedule.status)
				frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry_created', 0)
				frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry', '')
			else:
				je_doc = frappe.get_doc('Journal Entry', schedule.journal_entry)
				if je_doc.status != schedule.status:
					je_doc.db_set("status", schedule.status)

			if schedule.status != 'Return Cheque':
				je_doc = frappe.get_doc('Journal Entry', schedule.journal_entry)
				if je_doc.payment_entry:
					pe_doc = frappe.get_doc('Payment Entry', je_doc.payment_entry)
					if pe_doc.status_je != schedule.status:
						pe_doc.db_set("status_je", schedule.status)

		for charges in self.type_of_charges:
			if charges.status == 'Return Cheque':
				payment_doc = frappe.get_doc('Payment Entry', charges.payment_entry)
				payment_doc.db_set("status_je", charges.status)
				payment_doc.cancel()
				frappe.db.set_value(charges.doctype, charges.name, 'payment_entry_created', 0)
				frappe.db.set_value(charges.doctype, charges.name, 'payment_entry', '')

			if charges.status in ['Paid',"PDC Created"] and charges.payment_entry_created == 0:
				create_toc_payment_entry(self)

	def on_cancel(self):
		self.status == 'Disabled'
		frappe.db.set_value("Tenant Onboarding", self.name, {
			"status": "Disabled"
			})
		frappe.db.set_value('Unit', self.unit, 'status', 'Available')

		if self.payment_schedule:
			for i in self.payment_schedule:
				frappe.db.set_value(i.doctype, i.name, 'journal_entry_created', 0)
				frappe.db.set_value(i.doctype, i.name, 'journal_entry', '')
				frappe.db.set_value(i.doctype, i.name, 'payment_entry_created', 0)
				frappe.db.set_value(i.doctype, i.name, 'payment_entry', '')
				frappe.db.set_value(i.doctype, i.name, 'status', '')

		if self.type_of_charges:
			for m in self.type_of_charges:
				frappe.db.set_value(m.doctype, m.name, 'payment_entry_created', 0)
				frappe.db.set_value(m.doctype, m.name, 'payment_entry', '')
				self.reload()

		if self.deferred_revenue_schedule:
			for n in self.deferred_revenue_schedule:
				frappe.db.set_value(n.doctype, n.name, 'journal_entry_created', 0)
				frappe.db.set_value(n.doctype, n.name, 'journal_entry', '')

		if self.unit:
			frappe.db.set_value('Unit',self.unit,"status","Available")

		payment_entries = frappe.get_all('Payment Entry', filters={'tenant_onboarding': self.name, 'docstatus': 1})
		for i in payment_entries:
			pay_doc=frappe.get_doc("Payment Entry",i.name)
			pay_doc.cancel()


@frappe.whitelist()
def create_lease_agreement(customer, opportunity):
	opp_doc = frappe.get_doc("Opportunity", opportunity)
	lease_agreements = []
	for i in opp_doc.items:
		lease = frappe.get_doc(
			{
				"doctype": "Tenant Onboarding",
				"customer": customer,
				"unit": i.item_code,
				"payment_amount": float(i.amount),
				"opportunity": opportunity,
				"period_start_date": frappe.utils.nowdate(),
				"status": "Active"
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)
		lease_agreements.append(lease.name)

	return lease_agreements

@frappe.whitelist()
def create_customer(lead):
	lead = frappe.form_dict.lead
	
	lead_doc = frappe.get_doc("Lead", lead)
	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": lead_doc.lead_name,
			"customer_group": "Individual",
			"territory": lead_doc.territory,
			"disabled": 0
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)
	frappe.response['customer'] = customer.name

def populate_payment_schedule(doc):
	if not doc.period_start_date:
			frappe.throw(_("Period Start Date is mandatory"))

	end_num = doc.number
	if doc.number and doc.period:
		if doc.period == 'Year':
			end_num = doc.number * 12
			days = doc.number * 365
			doc.period_end_date =  frappe.utils.add_days(frappe.utils.add_months(doc.period_start_date, end_num),-1)
		elif doc.period=='Month':
			doc.period_end_date = frappe.utils.add_days(frappe.utils.add_months(doc.period_start_date, end_num),-1)

	if doc.number and doc.payment_frequency:
		doc.payment_schedule = []
		grand_total = doc.payment_amount * end_num
		total_amount = doc.payment_amount
		period = end_num
		n = 0
		if doc.payment_frequency == 'Yearly':
			total_amount = doc.payment_amount
			n = 1
			period = int(end_num / 12)
		elif doc.payment_frequency == 'Quaterly':
			total_amount = doc.payment_amount / 4
			n = 1
			period = int(end_num / 3)
		elif doc.payment_frequency == 'Half-yearly':
			total_amount = doc.payment_amount / 2
			n = 1
			period = int(end_num/ 6)
		elif doc.payment_frequency == 'Bimonthly':
			total_amount = doc.payment_amount / 6
			n = 1
			period = int(end_num/ 2)
		else:
			total_amount = doc.payment_amount/12
			n = 1

		if int(period) > 0:
			for x in range(period):
				j = n
				if doc.payment_frequency == 'Yearly':
					j = j + 12
				elif doc.payment_frequency == 'Monthly':
					j = j+1
				elif doc.payment_frequency == 'Quaterly':
					j = j+3
				elif doc.payment_frequency == 'Bimonthly':
					j = j+2
				else:
					j = j+6

				doc.append(
					"payment_schedule",
					{
						"payment_scheduled_date": frappe.utils.add_months(doc.period_start_date, n-1),
						"payment_amount": total_amount,
						"mode_of_payment": doc.mode_of_payment,
						# "reference_date": frappe.utils.add_months(doc.period_start_date, n-1),
						"cheque_end_date" : frappe.utils.add_months(frappe.utils.add_months(doc.period_start_date, n-1),6),
						"deferred_revenue_account" : doc.deferred_revenue_account,
						"service_start_date" : frappe.utils.add_months(doc.period_start_date, n-1),
						"service_end_date" :  frappe.utils.add_days(frappe.utils.add_months(doc.period_start_date, j-1), -1)
					},
				)
				if doc.payment_frequency == 'Yearly':
					n = n + 12
				elif doc.payment_frequency == 'Monthly':
					n = n+1
				elif doc.payment_frequency == 'Quaterly':
					n = n+3
				elif doc.payment_frequency == 'Bimonthly':
					n = n+2
				else:
					n = n+6
		total_scheduled_amount = period * total_amount
		# if total_scheduled_amount < grand_total:
		# 	doc.append(
		# 		"payment_schedule",
		# 		{
		# 			"payment_scheduled_date": doc.period_end_date,
		# 			"payment_amount": grand_total - total_scheduled_amount,
		# 			"mode_of_payment": doc.mode_of_payment,
		# 		},
		# 	)
	# k=0
	# for i in doc.payment_schedule:
	# 	k = k + i.payment_amount
	# 	doc.total = k
def populate_deferred_revenue_schedule(doc):
	if doc.payment_frequency != "Monthly":
		no_of_months = get_months(getdate(doc.period_start_date),getdate(get_last_day(doc.period_end_date)))
		first_month_rent_days = date_diff(get_last_day(doc.period_start_date),doc.period_start_date)
		rent_per_day = doc.payment_amount/365
		monthly_rent = doc.monthly_rent
		if first_month_rent_days < 27:
			first_month_rent = rent_per_day * first_month_rent_days
		elif first_month_rent_days >= 27:
			first_month_rent = monthly_rent
		last_month_rent = ((doc.number*doc.payment_amount)-(((no_of_months-2)*monthly_rent)+first_month_rent))

		for x in range(no_of_months):
			if x == 0:
				doc.append(
						"deferred_revenue_schedule",
						{
							"start_date": doc.period_start_date,
							"end_date": frappe.utils.add_months(get_last_day(doc.period_start_date),x),
							"payment_date": frappe.utils.add_months(get_last_day(doc.period_start_date),x),
							"rent": first_month_rent
						},
					)
			elif x == no_of_months-1 and last_month_rent != 0:
				doc.append(
					"deferred_revenue_schedule",
					{
						"start_date": get_first_day(frappe.utils.add_months(get_last_day(doc.period_start_date),x)),
						"end_date": doc.period_end_date,
						"payment_date": doc.period_end_date,
						"rent": last_month_rent
					},
				)
			else:
				doc.append(
					"deferred_revenue_schedule",
					{
						"start_date": get_first_day(frappe.utils.add_months(get_last_day(doc.period_start_date),x)),
						"end_date": get_last_day(frappe.utils.add_months(get_last_day(doc.period_start_date),x)),
						"payment_date": get_last_day(frappe.utils.add_months(get_last_day(doc.period_start_date),x)),
						"rent": monthly_rent
					},
				)

@frappe.whitelist()
def create_tenancy_contract(args):
	args = json.loads(args)
	to_doc = frappe.get_doc('Tenant Onboarding', args.get("name"))
	tc = frappe.new_doc('Tenancy Contract')
	tc.name_of_tenant = args.get("customer")
	tc.property_name = args.get("building")
	tc.unit_number = args.get("unit")
	tc.tenant_onboarding = args.get("name")
	tc.rent_in_aed = args.get("total")
	tc.period_start_date = to_doc.period_start_date
	tc.number =to_doc.number
	tc.period_end_date = to_doc.period_end_date
	tc.period = to_doc.period
	tc.payment_amount = to_doc.payment_amount
	tc.monthly_rent_amount = to_doc.monthly_rent
	tc.mode_of_payment = to_doc.mode_of_payment
	tc.tenant_address = to_doc.tenant_address
	for i in to_doc.payment_schedule:
		tc.append('payment_schedule', {
					'payment_scheduled_date': i.payment_scheduled_date,
					'payment_amount' : i.payment_amount,
					'paid_amount' : i.paid_amount,
					'status' : i.status,
					'payment_entry_created' : i.payment_entry_created,
					'mode_of_payment' : i.mode_of_payment,
					'reference_number' : i.reference_number,
					'reference_date': i.reference_date,
					'cheque_attachment': i.cheque_attachment,
					'ready_to_pay': i.ready_to_pay,
					'bank':i.bank
				})
	for k in to_doc.type_of_charges:
		tc.append('type_of_charges', {
					'particulars': k.particulars,
					'refund' : k.refund,
					'amount' : k.amount,
					'vat_percent' : k.vat_percent,
					'tax' : k.tax,
					'mode_of_payment':k.mode_of_payment,
					'account':k.account,
					'bank':k.bank,
					'reference_number':k.reference_number,
					'reference_date':k.reference_date
				})
	tc.total = to_doc.total
	tc.save()
	if tc:
		return tc.name

def create_toc_payment_entry(doc):
	pay_exc_acc = frappe.db.get_value('Account',(frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') else frappe.db.get_value('Company', doc.company, 'default_receivable_account')),'account_currency')
	pay_exc_rate = get_exchange_rate(pay_exc_acc, frappe.db.get_value('Company', doc.company, 'default_currency'), doc.posting_date)
	for toc in doc.type_of_charges:
		if not toc.mode_of_payment:
			mfp_account = frappe.db.get_value("Mode of Payment Account",{"parent": toc.mode_of_payment,"company": doc.company},"default_account")
		else:
			mfp_account=toc.account_paid_to
		if not mfp_account:
			frappe.throw(f"Default account not set in mode of payment {get_link_to_form('Mode of Payment', toc.mode_of_payment)} for company {frappe.bold(doc.company)}")
		paid_to_account_currency = frappe.db.get_value('Account',{'name' : mfp_account}, 'account_currency')
		cost_center = frappe.db.get_value("Company",doc.company,"cost_center")
		if not toc.payment_entry_created:
			pe_doc = frappe.new_doc("Payment Entry")
			pe_doc.payment_type = "Receive"
			pe_doc.posting_date = doc.posting_date
			pe_doc.company = doc.company
			pe_doc.mode_of_payment = toc.mode_of_payment
			pe_doc.is_pdc = 1 if toc.mode_of_payment == "PDC" else 0
			pe_doc.party_type = "Customer"
			pe_doc.party = doc.customer
			pe_doc.paid_from = toc.account
			pe_doc.paid_to = mfp_account
			pe_doc.paid_to_account_currency = paid_to_account_currency
			pe_doc.paid_amount = toc.amount
			pe_doc.received_amount = toc.amount
			pe_doc.customer = doc.customer
			pe_doc.unit = doc.unit
			pe_doc.property=doc.building
			pe_doc.reference_no = toc.reference_number
			pe_doc.reference_date = toc.reference_date
			pe_doc.status_je = toc.status
			pe_doc.cost_center = cost_center
			pe_doc.target_exchange_rate = pay_exc_rate
			pe_doc.tenant_onboarding = doc.name
			if toc.status == "PDC Created":
				pe_doc.is_pdc=1
			pe_doc.save()
			pe_doc.submit()
			frappe.db.set_value(toc.doctype, toc.name, 'payment_entry_created', 1)
			frappe.db.set_value(toc.doctype, toc.name, 'payment_entry', pe_doc.name)
			if toc.status == 'Paid':
				frappe.db.set_value(toc.doctype, toc.name, 'status', 'Cleared')
			doc.reload()


	for schedule in  doc.payment_schedule:
		if schedule.journal_entry_created == 0:
			journal_entry_doc = frappe.new_doc('Journal Entry')
			journal_entry_doc.company = doc.company
			journal_entry_doc.posting_date = doc.posting_date
			journal_entry_doc.tenant_onboarding = doc.name
			journal_entry_doc.status = schedule.status
			journal_entry_doc.cheque_no = schedule.reference_number
			journal_entry_doc.cheque_date = schedule.reference_date
			acc_type = frappe.db.get_value("Account",doc.deferred_revenue_account if doc.payment_frequency != 'Monthly' else frappe.db.get_value('Company', doc.company, 'default_rental_income'),"account_type")
			if acc_type == "Receivable":
				journal_entry_doc.append("accounts", {
					'party_type': "Customer",
					'party': doc.customer,
					'account': doc.deferred_revenue_account if doc.payment_frequency != 'Monthly' else frappe.db.get_value('Company', doc.company, 'default_rental_income'),
					'credit_in_account_currency': schedule.payment_amount,
					'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
					'unit':doc.unit,
					'customer':doc.customer,
					'property':doc.building
				})
			else:
				journal_entry_doc.append("accounts", {
					'account': doc.deferred_revenue_account if doc.payment_frequency != 'Monthly' else frappe.db.get_value('Company', doc.company, 'default_rental_income'),
					'credit_in_account_currency': schedule.payment_amount,
					'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
					'unit':doc.unit,
					'customer':doc.customer,
					'property':doc.building
				})
			acc_type =frappe.db.get_value("Account",frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') else frappe.db.get_value('Company', doc.company, 'default_receivable_account'),"account_type")
			if acc_type == "Receivable":
				journal_entry_doc.append("accounts", {
					'party_type': "Customer",
					'party': doc.customer,
					'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
					'account':frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') else frappe.db.get_value('Company', doc.company, 'default_receivable_account'),
					'debit_in_account_currency':  schedule.payment_amount,
					'unit':doc.unit,
					'customer':doc.customer,
					'property':doc.building
				})
			else:
				journal_entry_doc.append("accounts", {
					'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
					'account':frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') else frappe.db.get_value('Company', doc.company, 'default_receivable_account'),
					'debit_in_account_currency':  schedule.payment_amount,
					'unit':doc.unit,
					'customer':doc.customer,
					'property':doc.building
				})
			journal_entry_doc.submit()
			frappe.db.set_value(schedule.doctype, schedule.name, 'journal_entry_created', 1)
			frappe.db.set_value(schedule.doctype, schedule.name, 'journal_entry', journal_entry_doc.name)

	if  doc.deferred_revenue_schedule:
		for def_rev in doc.deferred_revenue_schedule:
			if getdate(def_rev.payment_date) < getdate(nowdate()):
				journal_entry_doc = frappe.new_doc('Journal Entry')
				journal_entry_doc.company = doc.company
				journal_entry_doc.posting_date = def_rev.payment_date
				journal_entry_doc.tenant_onboarding = doc.name
				acc_type = frappe.db.get_value("Account",frappe.db.get_value('Company', doc.company, 'default_rental_income'),"account_type")
				if acc_type == "Receivable":
					journal_entry_doc.append("accounts", {
						'party_type': "Customer",
						'party': doc.customer,
						'account': frappe.db.get_value('Company', doc.company, 'default_rental_income'),
						'credit_in_account_currency': def_rev.rent,
						'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
						'unit':doc.unit,
						'customer':doc.customer,
						'property':doc.building
					})
				else:
					journal_entry_doc.append("accounts", {
						'account': frappe.db.get_value('Company', doc.company, 'default_rental_income'),
						'credit_in_account_currency': def_rev.rent,
						'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
						'unit':doc.unit,
						'customer':doc.customer,
						'property':doc.building
					})
				acc_type = frappe.db.get_value("Account",doc.deferred_revenue_account,"account_type")
				if acc_type == "Receivable":
					journal_entry_doc.append("accounts", {
						'party_type': "Customer",
						'party': doc.customer,
						'account':  doc.deferred_revenue_account,
						'debit_in_account_currency':  def_rev.rent,
						'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
						'unit':doc.unit,
						'customer':doc.customer,
						'property':doc.building
					})
				else:
					journal_entry_doc.append("accounts", {
						'account':  doc.deferred_revenue_account,
						'debit_in_account_currency':  def_rev.rent,
						'cost_center': frappe.db.get_value('Company', doc.company, 'cost_center'),
						'unit':doc.unit,
						'customer':doc.customer,
						'property':doc.building
					})
				journal_entry_doc.submit()
				frappe.db.set_value(def_rev.doctype, def_rev.name, 'journal_entry_created', 1)
				frappe.db.set_value(def_rev.doctype, def_rev.name, 'journal_entry', journal_entry_doc.name)

@frappe.whitelist()
def create_payment_entry(doc):
	import json
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe._dict(doc)

	je_paid = frappe.db.sql('''
		SELECT
			je.name as name,
			SUM(je.total_credit) as total_credit,
			je.total_credit as total_amount
		FROM
			`tabJournal Entry` as je
		WHERE
			je.pe_created =0 AND je.docstatus = 1 AND je.tenant_onboarding = %s AND je.status = "Paid" ''',
	(doc.name),as_dict=1)

	pe = frappe.new_doc('Payment Entry')
	pe.voucher_type = 'Payment Entry'
	pe.company = doc.company
	pe.posting_date = getdate()
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = doc.customer
	pe.paid_amount = je_paid[0].total_amount
	pe.received_amount = je_paid[0].total_amount
	pe.tenant_onboarding = doc.name
	pe.status_je = 'Paid'
	# pe.mode_of_payment = 'Cash'
	pe.custom_remarks = True
	pe.setup_party_account_field()
	pe.set_missing_values()
	pe.set_missing_ref_details()
	return pe.as_dict()

@frappe.whitelist()
def create_payment_entry_pdc_created(doc):
	import json
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe._dict(doc)

	je_pdc_created = frappe.db.sql('''
		SELECT
			je.name as name,
			SUM(je.total_credit) as total_credit,
			je.total_credit as total_amount
		FROM
			`tabJournal Entry` as je
		WHERE
			je.pe_created =0 AND je.docstatus = 1 AND je.tenant_onboarding = %s AND je.status = "PDC created" ''',
	(doc.name),as_dict=1)

	pe = frappe.new_doc('Payment Entry')
	pe.voucher_type = 'Payment Entry'
	pe.company = doc.company
	pe.posting_date = getdate()
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = doc.customer
	pe.paid_amount = je_pdc_created[0].total_amount
	pe.received_amount = je_pdc_created[0].total_amount
	pe.tenant_onboarding = doc.name
	pe.status_je = 'PDC Created'
	# pe.mode_of_payment = 'Cheque'
	pe.custom_remarks = True
	pe.setup_party_account_field()
	pe.set_missing_values()
	pe.set_missing_ref_details()
	return pe.as_dict()

def get_months(start_date, end_date):
  diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
  return diff + 1

@frappe.whitelist()
def monthly_scheduler():
	def_rev = frappe.db.sql('''
	SELECT
		drs.name as name,
		drs.parent as parent,
		drs.parenttype as parenttype,
		drs.payment_date as pay_date,
		drs.rent as rent
	FROM
		`tabDeferred Revenue Schedule` as drs
	WHERE
		drs.journal_entry_created =0 AND drs.docstatus = 1 AND drs.parenttype = "Tenant Onboarding" AND drs.terminated = 0 ''',as_dict=1)
	if def_rev:
		for dr in def_rev:
			if str(frappe.utils.nowdate()) == str(dr.get('pay_date')):
				journal_entry_doc = frappe.new_doc('Journal Entry')
				journal_entry_doc.company = frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company')
				journal_entry_doc.posting_date = frappe.utils.nowdate()
				journal_entry_doc.tenant_onboarding = dr.get('parent')
				acc_type = frappe.db.get_value("Accounr",frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'default_rental_income'),"account_type")
				if acc_type == "Receivable":
					journal_entry_doc.append("accounts", {
						'party_type': "Customer",
						'party': frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'account': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'default_rental_income'),
						'credit_in_account_currency': dr.get('rent'),
						'cost_center': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'cost_center'),
						'unit':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'unit'),
						'customer':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'property':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'building')

					})
				else:
					journal_entry_doc.append("accounts", {
						'account': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'default_rental_income'),
						'credit_in_account_currency': dr.get('rent'),
						'cost_center': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'cost_center'),
						'unit':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'unit'),
						'customer':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'property':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'building')

				})
				acc_type = 	frappe.db.get_value("Account",frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'deferred_revenue_account'),"account_type")
				if acc_type == "Receivable":
					journal_entry_doc.append("accounts", {
						'party_type': "Customer",
						'party': frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'account': frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'deferred_revenue_account'),
						'debit_in_account_currency':  dr.get('rent'),
						'cost_center': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'cost_center'),
						'unit':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'unit'),
						'customer':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'property':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'building')
					})
				else:
					journal_entry_doc.append("accounts", {
						'account': frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'deferred_revenue_account'),
						'debit_in_account_currency':  dr.get('rent'),
						'cost_center': frappe.db.get_value('Company', frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'company'), 'cost_center'),
						'unit':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'unit'),
						'customer':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'customer'),
						'property':frappe.db.get_value('Tenant Onboarding', dr.get('parent'), 'building')
					})
				journal_entry_doc.submit()
				frappe.db.set_value('Deferred Revenue Schedule', dr.get('name'), 'journal_entry_created', 1)
				frappe.db.set_value('Deferred Revenue Schedule', dr.get('name'), 'journal_entry', journal_entry_doc.name)
			else:
				pass

@frappe.whitelist()
def cancel_tenant_onboarding(doc, values):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe._dict(doc)
	to_doc = frappe.get_doc('Tenant Onboarding', doc.name)
	toc = frappe.new_doc('Tenant Onboarding Termination')
	toc.customer = doc.customer
	toc.property = doc.building
	toc.unit = doc.unit
	toc.company = doc.company
	toc.period_start_date = doc.period_start_date
	toc.period_end_date = doc.period_end_date
	toc.termination_date = getdate(values)
	toc.tenant_onboarding = doc.name
	toc.total_amount = doc.payment_amount*doc.number
	toc.number_of_years=doc.number
	occupied_rent = 0

	for i in to_doc.deferred_revenue_schedule:
		remaining_rent = 0

		if toc.termination_date > i.end_date:
			occupied_rent  = occupied_rent + i.rent

		if i.start_date <= getdate(values)<= i.end_date:
			days = date_diff(getdate(values),i.start_date)
			total_days = date_diff(i.end_date, i.start_date)
			per_day_rent =  i.rent/(total_days+1)
			rent = (days+1) * per_day_rent
			remaining_rent = i.rent - rent
			toc.append(
				"rental_income",
				{
					"start_date": i.start_date,
					"end_date": getdate(values),
					"payment_date": getdate(values),
					"rent": rent
				},
			)
			if toc.termination_date == i.end_date:
				pass
			else:
				toc.append(
					"reverse_deferred_revenue",
					{
						"start_date": frappe.utils.add_days(getdate(values), 1),
						"end_date":i.end_date,
						"payment_date": i.end_date,
						"rent": remaining_rent
					},
				)
			toc.occupied_rent = occupied_rent + rent

		elif getdate(values) < i.end_date:
			toc.append(
				"reverse_deferred_revenue",
				{
					"start_date":i.start_date,
					"end_date":i.end_date,
					"payment_date": i.end_date,
					"rent": i.rent
				},
			)

	deposits = 0
	clr_depo=0
	pdc_depo=0
	for m in to_doc.type_of_charges:
		if m.refund == 'Yes':
			deposits = deposits + m.amount
			if m.status == "Cleared":
				clr_depo=clr_depo+m.amount
			if m.status == "PDC Created":
				pdc_depo=pdc_depo+m.amount
	toc.security_deposits = deposits

	unoccupied_rent = 0
	for un_rent in toc.reverse_deferred_revenue:
		unoccupied_rent += un_rent.rent

	toc.unoccupied_rent = unoccupied_rent
	toc.total_refu = deposits + unoccupied_rent
	status=""
	cleared=0
	pdc=0
	toc.payment_schedule=None
	for i in to_doc.payment_schedule:
		if i.status == "PDC Created":
			status ="Return Cheque"
		if i.status == "Cleared":
			status="Cleared"
		toc.append(
			"payment_schedule",
				{
					"payment_scheduled_date":i.payment_scheduled_date,
					"payment_amount":i.payment_amount,
					"paid_amount":i.paid_amount,
					"status":status,
					"mode_of_payment":i.mode_of_payment,
					"reference_number":i.reference_number,
					"reference_date":i.reference_date,
					"payment_entry_created":i.payment_entry_created	,
					"bank":i.bank,
					"account_paid_to":i.account_paid_to,
					"cheque_end_date":i.cheque_end_date
				},
		)
	
	if toc.payment_schedule:
		for i in toc.payment_schedule:
			if i.status == "Return Cheque":
				pdc+=i.payment_amount
			if i.status == "Cleared":
				cleared+=i.payment_amount

	cleared_refundable=flt(cleared)-flt(toc.occupied_rent)
	toc.refund_cleared=rounded(cleared_refundable,2)
	toc.refund_pdc=pdc+pdc_depo
	total_refundable=clr_depo+toc.refund_cleared
	toc.total_refundable = total_refundable
	toc.save()
	if toc:
		return toc.name

@frappe.whitelist()
def renew_tenant_onboarding(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = frappe._dict(doc)
	to_doc = frappe.new_doc('Tenant Onboarding')
	to_doc.customer = doc.customer
	to_doc.tenant_type = doc.tenant_type
	to_doc.tenant_address = doc.tenant_address
	to_doc.company = doc.company
	to_doc.building = doc.building
	to_doc.unit_nature = doc.unit_nature
	to_doc.posting_date = doc.posting_date
	to_doc.status = 'Renewed'
	to_doc.unit = doc.unit
	to_doc.sales_person = doc.sales_person
	to_doc.tenancy_application = doc.tenancy_application
	to_doc.remarks = doc.remarks
	to_doc.total = doc.total
	to_doc.deferred_revenue_account = doc.deferred_revenue_account
	to_doc.payment_frequency = doc.payment_frequency
	to_doc.mode_of_payment = doc.mode_of_payment
	to_doc.monthly_rent = doc.monthly_rent
	to_doc.payment_amount = doc.payment_amount
	to_doc.period = doc.period
	to_doc.number = doc.number
	to_doc.tenant_onboarding = doc.name
	to_doc.period_start_date = str(add_to_date(getdate(doc.period_start_date), years = 1))
	for i in doc.member_details:
		to_doc.append("member_details", {
			"name1": i.get('name1'),
			"relationship" : i.get('relationship'),
			"occupation" : i.get('occupation'),
			"age" : i.get('age'),
			"gender" : i.get('gender'),
			"dob" : i.get('dob'),
			"passport_expiry_date" : i.get('passport_expiry_date'),
			"passprt_no" : i.get('passprt_no'),
			"eid_no" : i.get('eid_no'),
			"eid_expiry_date" : i.get('eid_expiry_date'),
			"uid_no" : i.get('uid_no'),
			"visa_no" : i.get('visa_no')
		})
	for k in doc.type_of_charges:
		to_doc.append("type_of_charges",{
			"particulars" : k.get('particulars'),
			"account" : k.get('account'),
			"refund" : k.get('refund'),
			"amount" : k.get('amount'),
			"vat_percent" : k.get('vat_percent'),
			"tax" : k.get('tax'),
			"status" : k.get('status'),
			"payment_entry_created" : k.get('payment_entry_created'),
			"mode_of_payment" : k.get('mode_of_payment'),
			"reference_number" : k.get('reference_number'),
			"reference_date" : k.get('reference_date'),
			"cheque_end_date" : k.get('cheque_end_date'),
			"cheque_attachment" : k.get('cheque_attachment')
		})
	return to_doc.as_dict()

@frappe.whitelist()
def auto_create_payment_entry(docname):
	doc = frappe.get_doc("Tenant Onboarding", docname)

	exc_curr = frappe.db.get_value('Account',(frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') if frappe.db.get_value('Party Account',{'parent' : doc.customer, 'company': doc.company}, 'account') else frappe.db.get_value('Company', doc.company, 'default_receivable_account')),'account_currency')
	exc_rate = get_exchange_rate(exc_curr, frappe.db.get_value('Company', doc.company, 'default_currency'), doc.posting_date)
	for schedule in  doc.payment_schedule:
		schedule.payment_amount =  round(schedule.payment_amount, 2)
		if not schedule.mode_of_payment:
			paid_to_account = frappe.db.get_value('Mode of Payment Account',{'parent' : schedule.mode_of_payment, 'company': doc.company}, 'default_account')
		else:
			paid_to_account=schedule.account_paid_to
		if not paid_to_account and not schedule.status == "Unpaid":
			frappe.throw(f"Default account not set in mode of payment {get_link_to_form('Mode of Payment', schedule.mode_of_payment)} for company {frappe.bold(doc.company)}")
		paid_to_account_currency = frappe.db.get_value('Account',{'name' : paid_to_account}, 'account_currency')
		if schedule.payment_entry_created == 0 and schedule.status == 'PDC Created':
			je_pdc_created = frappe.db.sql('''
				SELECT
					je.name as name,
					SUM(je.total_credit) as total_credit,
					je.total_credit as total_amount
				FROM
					`tabJournal Entry` as je
				WHERE
					je.pe_created =0 AND je.docstatus = 1 AND je.tenant_onboarding = %s AND je.status = "PDC created" ''',
			(doc.name),as_dict=1)

			pe = frappe.new_doc('Payment Entry')
			pe.voucher_type = 'Payment Entry'
			pe.company = doc.company
			pe.posting_date =  schedule.reference_date
			pe.payment_type = "Receive"
			pe.party_type = "Customer"
			pe.mode_of_payment = schedule.mode_of_payment
			pe.party = doc.customer
			pe.paid_to = paid_to_account
			pe.paid_to_account_currency = paid_to_account_currency
			pe.tenant_onboarding = doc.name
			pe.received_amount = je_pdc_created[0].total_amount
			pe.paid_amount = je_pdc_created[0].total_amount
			pe.custom_remarks = True
			pe.reference_no = schedule.reference_number
			pe.reference_date = schedule.reference_date
			pe.status_je = schedule.status
			pe.target_exchange_rate = exc_rate
			pe.customer = doc.customer
			pe.unit = doc.unit
			pe.property = doc.building
			pe.is_pdc = True
			pe.append("references", {
				'reference_doctype': "Journal Entry",
				'reference_name': schedule.journal_entry,
				'total_amount' : schedule.payment_amount,
				'outstanding_amount': schedule.payment_amount,
				'allocated_amount' : schedule.payment_amount,
				'parenttype': "Payment Entry",
				'parentfield': "references",
			})
			pe.setup_party_account_field()
			pe.set_missing_values()
			pe.save()
			pe.submit()
			frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry_created', 1)
			frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry', pe.name)
			frappe.db.set_value('Journal Entry',  schedule.journal_entry, 'pe_created', 1)
			frappe.db.set_value('Journal Entry',  schedule.journal_entry, 'payment_entry', pe.name)

			frappe.msgprint(
				msg='Payment Entries(PDC) Created',)

		elif schedule.payment_entry_created == 0 and schedule.status == 'Paid':
			je_paid = frappe.db.sql('''
				SELECT
					je.name as name,
					SUM(je.total_credit) as total_credit,
					je.total_credit as total_amount
				FROM
					`tabJournal Entry` as je
				WHERE
					je.pe_created =0 AND je.docstatus = 1 AND je.tenant_onboarding = %s AND je.status = "Paid" ''',
			(doc.name),as_dict=1)
			pe = frappe.new_doc('Payment Entry')
			pe.voucher_type = 'Payment Entry'
			pe.company = doc.company
			pe.posting_date = schedule.reference_date
			pe.payment_type = "Receive"
			pe.party_type = "Customer"
			pe.mode_of_payment = schedule.mode_of_payment
			pe.party = doc.customer
			pe.paid_to = paid_to_account
			pe.paid_to_account_currency = paid_to_account_currency
			pe.tenant_onboarding = doc.name
			pe.status_je = schedule.status
			pe.received_amount = je_paid[0].total_amount
			pe.paid_amount = je_paid[0].total_amount
			pe.custom_remarks = True
			pe.reference_no = schedule.reference_number
			pe.reference_date = schedule.reference_date
			pe.target_exchange_rate = exc_rate
			pe.customer = doc.customer
			pe.unit = doc.unit
			pe.property = doc.building
			pe.append("references", {
				'reference_doctype': "Journal Entry",
				'reference_name': schedule.journal_entry,
				'total_amount' : schedule.payment_amount,
				'outstanding_amount': schedule.payment_amount,
				'allocated_amount' : schedule.payment_amount,
				'parenttype': "Payment Entry",
				'parentfield': "references",
			})
			pe.setup_party_account_field()
			pe.set_missing_values()
			pe.save()
			pe.submit()
			frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry_created', 1)
			frappe.db.set_value(schedule.doctype, schedule.name, 'payment_entry', pe.name)
			frappe.db.set_value('Journal Entry',  schedule.journal_entry, 'pe_created', 1)
			frappe.db.set_value('Journal Entry',  schedule.journal_entry, 'payment_entry', pe.name)
			frappe.db.set_value(schedule.doctype, schedule.name, 'status', 'Cleared')
			frappe.db.set_value(schedule.doctype, schedule.name, 'paid_amount',pe.paid_amount)

			frappe.msgprint(
				msg='Payment Entries(Paid) Created',)

@frappe.whitelist()
def cheque_status(pay_ref,to_name,pay_date,date,status,remarks,ref_no):
	if frappe.db.exists("Cheque Status",{"reference_number":pay_ref,"tenant_onboarding":to_name}):
		ch=frappe.get_doc("Cheque Status",{"reference_number":pay_ref,"tenant_onboarding":to_name})
		ch.append("cheque_status", {
			'reference_doctype': "Cheque Status Details",
			'date':date ,
			'status':status,
			'remarks':remarks,
			'reference_number':pay_ref,
			'tenant_onboarding':to_name,})
		ch.save()
	else:
		ch = frappe.new_doc('Cheque Status')
		ch.reference_number=pay_ref
		ch.tenant_onboarding=to_name
		ch.payment_date=pay_date
		ch.reference=ref_no
		ch.append("cheque_status", {
			'reference_doctype': "Cheque Status Details",
			'date':date ,
			'status':status,
			'remarks':remarks,
			'reference_number':pay_ref,
			'tenant_onboarding':to_name,
		})
		ch.save()

	cheque_details = frappe.get_all("Cheque Status Details",filters = {"reference_number":pay_ref,"tenant_onboarding":to_name},fields=["date","status","remarks"])
	return cheque_details

@frappe.whitelist()
def change_status():
	ten=frappe.db.get_all('Tenant Onboarding')
	for i in ten:
		doc=frappe.get_doc("Tenant Onboarding",i.name)
		if doc.period_end_date and doc.docstatus ==1 and doc.status != "Terminated":
			if doc.period_end_date < getdate(nowdate()):
				frappe.db.set_value("Tenant Onboarding",doc.name,"status","Expired", update_modified=False)