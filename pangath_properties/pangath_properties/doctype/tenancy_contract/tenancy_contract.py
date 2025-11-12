# Copyright (c) 2023, iterative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,getdate, add_days
from datetime import datetime, timedelta
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc


class TenancyContract(Document):
	def on_cancel(self):
		frappe.db.set_value('Unit', self.unit_number, 'status', 'Available') # update the unit status
		sales_inv = frappe.db.get_list('Sales Invoice', {'custom_tenancy_contract': self.name, 'docstatus': 1}, 'name')
		if sales_inv:
			frappe.throw(f"Cannot cancel the tenancy contract as there are sales invoices linked to it {sales_inv[0].name}. Please cancel the sales invoices first.")
			
	def on_trash(self):
		sales_inv = frappe.db.get_list('Sales Invoice', {'custom_tenancy_contract': self.name}, 'name')
		if sales_inv:
			frappe.throw(f"Cannot delete the tenancy contract as there are sales invoices linked to it {sales_inv[0].name}. Please delete the sales invoices first.")

		pdc = frappe.db.get_list('Post Dated Cheque', {'tenancy_contract': self.name}, 'name')
		if pdc:
			frappe.throw(f"Cannot delete the tenancy contract as there are post-dated cheques linked to it {pdc[0].name}. Please delete the post-dated cheques first.")

	def set_sch_pay_invoice_wise(self, data):
		freq = int(self.schedule_payments[-1].payment_frequency.split()[0])
		result = []
		for index in range(freq):
			curr_list = []
			for particular in data:
				# ensure index exists in the list
				if index < len(data[particular]):
					curr_list.append(data[particular][index])
			result.append(curr_list)
		return result

	

	def set_in_ps_row(self, si, amount, freq, unit, part, tax, acc):
		"""Append one item row to Sales Invoice"""
		rate = flt(amount / freq)
		si.append("items", {
			"item_code": unit,
			"qty": 1,
			"rate": rate,
			"description": part,
			"item_tax_template": tax,
			"income_account": acc,
			"cost_center": frappe.db.get_value("Company", self.company, "cost_center")
		})

	def on_submit(self):
		posting_date = nowdate()
		freq = self.schedule_payments[-1].number_of_period
		cost_center = frappe.db.get_value("Company", self.company, "cost_center")
		all_units = [unit.unit for unit in self.unit_details]
		for unit_det in self.unit_details:
			frappe.db.set_value('Unit', unit_det.unit, 'status', 'Rented')

		if self.is_multiple_invoices:		
			unit_count = len(self.unit_details)
			si_list = []
			#adding doctype fields for each
			for pay_sch in self.payment_schedule: #takin pay_sch each row for si main doc details =>1
					si_doc = frappe.get_doc({
						"doctype": "Sales Invoice",
						"customer": self.name_of_tenant,
						"set_posting_time": 1,
						"posting_date": pay_sch.payment_scheduled_date,
						"due_date": add_days(pay_sch.payment_scheduled_date, 14),
						"custom_tenancy_contract": self.name,
						"cost_center": cost_center
					})
					si_list.append(si_doc)

			#against each payment schedule add rows = unit count
			for idx, pay_sch in enumerate(self.payment_schedule): #takin pay_sch each row for respective child item => 2 
				for unit_info in self.unit_details:
					self.set_in_ps_row(
						si_list[idx],
						pay_sch.payment_amount,
						unit_count,
						unit_info.unit,
						"Rent",
						pay_sch.get('item_tax_detail', ""),
						pay_sch.income_account
					)
				frappe.db.set_value("TC Payment Schedule", pay_sch.name, "is_accrued", 1)

			if si_list[0]:# add all type of charges
				for row in self.type_of_charges:
					if not frappe.db.exists("Item", row.particulars):
						item = frappe.new_doc("Item")
						item.name = row.particulars
						item.item_code = row.particulars
						item.item_group = "Services"
						item.maintain_stock = 0
						item.save()

					si_list[0].append("items", {
						"item_code": row.particulars,
						"qty": 1,
						"rate": row.amount,
						"description": row.particulars,
						"item_tax_template": row.item_tax_template,
						"income_account": row.account,
						"cost_center": cost_center
					})
			
			for si in si_list:
				if si.items:
					si.insert()
					if si.taxes:
						for t in si.taxes:
							t.cost_center = cost_center
					si.submit()
			
			
			frappe.msgprint("Sales Invoices successfully created with rent")
		else:
			single_si = frappe.get_doc({
						"doctype": "Sales Invoice",
						"customer": self.name_of_tenant,
						"set_posting_time": 1,
						"posting_date": self.payment_schedule[0].payment_scheduled_date,
						"due_date": add_days(self.payment_schedule[0].payment_scheduled_date, 14),
						"custom_tenancy_contract": self.name,
						"cost_center": cost_center
					})
			
			
			for unit in self.unit_details:
					single_si.append("items",{
						"item_code": unit.unit,
						"qty": 1,
						"rate": unit.rent_amount,
						"description": "Rent",
						"item_tax_template": self.payment_schedule[0].item_tax_template,
						"income_account": self.payment_schedule[0].income_account,
						"cost_center": cost_center
					})
			
			for row in self.type_of_charges:
				if not frappe.db.exists("Item", row.particulars):
						item = frappe.new_doc("Item")
						item.name = row.particulars
						item.item_code = row.particulars
						item.item_group = "Services"
						item.maintain_stock = 0
						item.save()
				
				single_si.append("items",{
						"item_code": row.particulars,
						"qty": 1,
						"rate": row.amount,
						"description": row.particulars,
						"item_tax_template": row.item_tax_template,
						"income_account": row.account,
						"cost_center": cost_center
				})

			single_si.save()
			if single_si.taxes:
				for row in single_si.taxes:
					row.cost_center = cost_center
			single_si.submit()
		# for idx, i in enumerate(self.payment_schedule):
		#     if i.is_pdc == 1:
		#         account = frappe.db.get_value('Bank Account', {'name':i.bank_account}, 'account')
		#         pdc = frappe.get_doc({
		#             "doctype": "Post Dated Cheque",
		#             "party_type": "Customer",
		#             "party": self.name_of_tenant,
		#             "posting_date": i.payment_scheduled_date,
		#             "bank": i.bank,
		#             "bank_account":account if i.bank_account else "",
		#             "cheque_amount": i.payment_amount,
		#             "cheque__no": i.cheque_number,
		#             "tenancy_contract": self.name,
		#             "status":"Received",
		#             #"unit":self.unit_number,
		#             "property":self.property_name,
		#             "amount_in_words":frappe.utils.money_in_words(i.payment_amount),
		#             "date_of_issue":i.date_of_issue,
		#             "expiry_date":i.expiry_date,
		#             "cheque_date":i.cheque_date,
		#             "reference":i.name,
		#             "sales_invoice":sinv_name
		#         })
		#         pdc.append(
		#             "cheque_audit_trail",
		#             {
		#                 "transaction_date": i.payment_scheduled_date,
		#                 "status": "Received",
		#                 "remarks":"Cheque Received"
		#             },
		#         )
		#         pdc.insert()
		#         pdc.submit()
		#         frappe.db.commit()
				# frappe.db.set_value("TC Payment Schedule", i.name, "pdc",pdc.name)
				# -------------------- based on the requiremnt - creating sales invoice in single invoice --------------
			# posting_date = nowdate()
			# vat = frappe.db.get_value('Sales Taxes and Charges Template',{'company':self.company,'is_default':1},'name') 
			# if idx + 1 < len(self.payment_schedule):
			#     next_payment_scheduled_date = self.payment_schedule[idx + 1].payment_scheduled_date
			# else:
			#     next_payment_scheduled_date = frappe.db.get_value("TA Payment Schedule",{"parent":self.name},"period_end_date")
			# # Handle Sales Invoice
			# if str(i.payment_scheduled_date) == str(posting_date):
			#     if i.idx  == 1 and i.is_accrued ==0 :
			#         create_si_idx(i, vat, self, next_payment_scheduled_date)
			#     sales_invoice = frappe.get_doc({
			#         "doctype": "Sales Invoice",
			#         "customer": self.name_of_tenant,
			#         "set_posting_time":1,
			#         "posting_date": i.payment_scheduled_date,
			#         "due_date": i.payment_scheduled_date if str(i.payment_scheduled_date) <= posting_date else posting_date,
			#         "property": self.property_name,
			#         "unit": self.unit_number,
			#         "custom_tenancy_contract": self.name,
			#         "items": [
			#             {
			#                 "item_code": self.unit_number,
			#                 "qty": 1,
			#                 "rate": i.payment_amount,
			#                 "property": self.property_name,
			#                 "unit": self.unit_number,
			#                 "enable_deferred_revenue": 1,
			#                 "service_start_date": i.payment_scheduled_date,
			#                 "service_end_date": next_payment_scheduled_date  # Use next payment date or period_end_date
			#             }
			#         ]
			#     })
			#     sales_invoice.insert()
			#     sales_invoice.submit()
			#     frappe.db.set_value("TC Payment Schedule", i.name, "is_accrued", 1)
			#     frappe.db.set_value("TC Payment Schedule", i.name, "sales_invoice", sales_invoice.name)
			# else:
			#     sales_invoice = frappe.get_doc({
			#         "doctype": "Sales Invoice",
			#         "customer": self.name_of_tenant,
			#         "set_posting_time":1,
			#         "posting_date": nowdate(),
			#         "due_date": i.payment_scheduled_date,
			#         "property": self.property_name,
			#         "unit": self.unit_number,
			#         "custom_tenancy_contract": self.name,
			#         "items": [
			#             {
			#                 "item_code": self.unit_number,
			#                 "qty": 1,
			#                 "rate": i.payment_amount,
			#                 "property": self.property_name,
			#                 "unit": self.unit_number,
			#                 "enable_deferred_revenue": 1,
			#                 "service_start_date": i.payment_scheduled_date,
			#                 "service_end_date": next_payment_scheduled_date  # Use next payment date or period_end_date
			#             }
			#         ]
			#     })
			#     sales_invoice.insert()
			#     sales_invoice.submit()
			#     frappe.db.set_value("TC Payment Schedule", i.name, "is_accrued", 1)
			#     frappe.db.set_value("TC Payment Schedule", i.name, "sales_invoice", sales_invoice.name)


		# for i in self.type_of_charges:
		#     sales_invoice = frappe.get_doc({
		#             "doctype": "Sales Invoice",
		#             "customer": self.name_of_tenant,
		#             "property": self.property_name,
		#             "unit": self.unit_number,
		#             "custom_tenancy_contract": self.name,
		#             "set_posting_time":1,
		#             "posting_date": i.payment_date,
		#             "due_date": i.payment_date,
		#             "debit_to":i.account,
		#             "items": [
		#                 {
		#                     "item_code": self.unit_number,
		#                     "qty": 1,
		#                     "rate": i.amount,
		#                     "property": self.property_name,
		#                     "unit": self.unit_number,
		#                 }
		#             ]
		#         })
		#     sales_invoice.insert()
		#     sales_invoice.submit()

		#     frappe.db.set_value("Type Of Charges", i.name, "is_accrued", 1)
		#     frappe.db.set_value("Type Of Charges", i.name, "sales_invoice", sales_invoice.name)

	#         if i.is_pdc == 1:
	#                 pdc = frappe.get_doc({
	#                     "doctype": "Post Dated Cheque",
	#                     "party_type": "Customer",
	#                     "party": self.name_of_tenant,
	#                     "posting_date": i.payment_date,
	#                     "bank": i.bank,
	#                     "cheque_amount": i.amount,
	#                     "cheque__no": i.payment_date,
	#                     "tenancy_contract": self.name,
	#                     "status":"Received",
	#                     #"unit":self.unit_number,
	#                     "property":self.property_name,
	#                     "amount_in_words":frappe.utils.money_in_words(i.amount),
	#                     "date_of_issue":i.reference_date,
	#                     "expiry_date":i.cheque_end_date,
	#                     "cheque_date":i.reference_date,
	#                     "reference":i.name,
	#                     "sales_invoice":sinv_name
	#                 })
	#                 pdc.append(
	#                     "cheque_audit_trail",
	#                     {
	#                         "transaction_date": i.payment_date,
	#                         "status": "Received",
	#                         "remarks":"Cheque Received"
	#                     },
	#                 )
	#                 pdc.insert()
	#                 pdc.submit()
	#                 frappe.db.set_value("TC Payment Schedule", i.name, "pdc",pdc.name)


	#     if frappe.db.get_value("Customer",self.name_of_tenant,"lead_name"):
	#         frappe.db.set_value("Lead",frappe.db.get_value("Customer",self.name_of_tenant,"lead_name"),"status","Tenancy Contract")
			
	#     #  update the status in Opportunity 
	#     if self.opportunity:
	#         frappe.db.set_value("Opportunity",self.opportunity,"status","Tenancy Contract")

	#     frappe.db.set_value("Customer",self.name_of_tenant,"property_name",self.property_name)
	#     #frappe.db.set_value("Customer",self.name_of_tenant,"unit_name",self.unit_number)
	#     #if self.unit_number:
	#         # doc = frappe.get_doc("Unit", self.unit_number)
	#         # doc.status = "Rented"
	#         # doc.save()

	from datetime import timedelta
	from frappe.utils import getdate, nowdate, flt, add_days
	
	def validate(self):
		from frappe.utils import getdate, add_days, flt
		if self.payment_schedule:
			tot_amt = 0
			for row in self.payment_schedule:
				tot_amt += row.payment_amount
			if int(tot_amt) != int(self.yearly_rent):
				frappe.throw(f'Total Payment amount should be {self.yearly_rent}')
		
		# Ensure contract dates are date objects
		# if not self.is_new():
		#     contract_start = getdate(self.contract_start_date)
		#     contract_end = getdate(self.contract_end_date)

		#     # Validate service_end_date against contract period
		#     # Validate that the first and last service_end_date are within contract period
		#     if self.payment_schedule:
		#         first_service_start = getdate(self.payment_schedule[0].service_start_date)
		#         last_service_end = getdate(self.payment_schedule[-1].service_end_date)
		#         if not (contract_start <= first_service_start <= contract_end):
		#             frappe.throw(
		#                 f'First service start date {frappe.utils.format_date(first_service_start)} must be within the contract period '
		#                 f'{frappe.utils.format_date(contract_start)} to {frappe.utils.format_date(contract_end)}'
		#             )
		#         if not (contract_start <= last_service_end <= contract_end):
		#             frappe.throw(
		#                 f'Last service end date {frappe.utils.format_date(last_service_end)} must be within the contract period '
		#                 f'{frappe.utils.format_date(contract_start)} to {frappe.utils.format_date(contract_end)}'
		#             )

		# Run your custom methods
		calculate_schedule_tax(self)
		populate_payment_schedule(self)

		# Fetch default accounts
		default_income_account = frappe.db.get_value("Company", self.company, "default_income_account")
		default_deferred_account = frappe.db.get_value("Company", self.company, "default_deferred_revenue_account")

		# Sort rows by scheduled date (use getdate for sorting safety)
		self.payment_schedule.sort(key=lambda x: getdate(x.payment_scheduled_date))

		# Use last payment_scheduled_date as fallback for end date
		# period_end_date = max(
		#     [getdate(d.payment_scheduled_date) for d in self.payment_schedule if d.payment_scheduled_date],
		#     default=None
		# )
		if self.schedule_payments:
			period_end_date = self.schedule_payments[0].period_end_date or ''

		# Process each payment_schedule row
		for idx, row in enumerate(self.payment_schedule):
			row.service_start_date = getdate(row.payment_scheduled_date)

			if idx + 1 < len(self.payment_schedule):
				# End = day before next payment starts
				next_payment_date = getdate(self.payment_schedule[idx + 1].payment_scheduled_date)
				row.service_end_date = add_days(next_payment_date, -1)
			else:
				# Last payment should end at period_end_date (contract end)
				if period_end_date:
					row.service_end_date = getdate(period_end_date)
				else:
					# fallback: 1 year from first payment start
					row.service_end_date = add_days(getdate(self.payment_schedule[0].payment_scheduled_date), 365 - 1)

			# Safety: Ensure start <= end
			if row.service_end_date < row.service_start_date:
				print(f"Warning: service_end_date {row.service_end_date} was before service_start_date {row.service_start_date}. Adjusting end date.")
				row.service_end_date = row.service_start_date

			# Set accounts
			row.income_account = default_income_account
			row.deffered_revenue_account = default_deferred_account

		# Calculate total = yearly rent + charges
		total = 0
		for i in self.type_of_charges:
			total += flt(i.amount)

		self.total = total + flt(self.yearly_rent)

		
	# def before_insert(self):
	#     customer = frappe.new_doc("Customer")
	#     customer.customer_name = self.name_of_tenant
	#     customer.save()
	#     self.name_of_tenant = customer.name

	def after_insert(self):
		#frappe.db.set_value("Tenancy Application",self.tenancy_application,"tenancy_contract",self.name)
		if self.proposal_agreement:
			frappe.db.set_value("Tenancy Application", self.proposal_agreement, "tenancy_contract", self.name)
		if self.booking_agreement:
			frappe.db.set_value("Lease Agreement", self.booking_agreement, "tenancy_contract", self.name)
		

	def before_save(self):
		pass
		# for i in self.payment_schedule:
		#     i.unit = self.unit_number
		#     i.property = self.property_name

	def on_update_after_submit(self):
		pass
		# for i in self.payment_schedule:
		#     if i.pdc:
		#         pdc = frappe.get_doc("Post Dated Cheque",i.pdc)
		#         if pdc:
		#             pdc.db_set("date_of_issue",i.date_of_issue)
		#             pdc.db_set("expiry_date",i.expiry_date)
		#             pdc.db_set("cheque_date",i.cheque_date)
		#             pdc.db_set("cheque__no",i.cheque_number)
		#             pdc.db_set("status",i.cheque_status)


		# for i in self.payment_schedule:
		#     if i.pdc:
		#         pdc = frappe.get_doc("Post Dated Cheque",i.pdc)
		#         if pdc:
		#             pdc.db_set("date_of_issue",i.date_of_issue)
		#             pdc.db_set("expiry_date",i.expiry_date)
		#             pdc.db_set("cheque_date",i.cheque_date)
		#             pdc.db_set("cheque__no",i.cheque_number)
		#             pdc.db_set("status",i.cheque_status)

def populate_payment_schedule(self):
	from frappe.utils import add_months, getdate, flt

	if not self.manual_schedule:
		if not self.payment_schedule:
			for i in self.schedule_payments:
				start_date = getdate(i.period_start_date) or getdate()
				payment_frequency = int(str(i.payment_frequency).split(" ")[0])  # e.g. "3 Payment" → 3
				
				interval = flt(i.number_of_period) or 1                # how many years/months
				total_amount = flt(self.yearly_rent) or 0              # yearly rent
				period_type = i.period_type                            # Year or Month

				# Validate frequency
				if not payment_frequency or payment_frequency < 1:
					frappe.throw("Payment Frequency must be between 1 and 6")

				if payment_frequency > 6:
					frappe.throw("Maximum allowed Payment Frequency is 6")

				# Clear previous entries to avoid duplicates
				self.payment_schedule = []

				# Determine total months based on period type
				if period_type == "Year":
					total_months = interval * 12
				elif period_type == "Month":
					total_months = interval
				else:
					frappe.throw("Invalid Period Type. Please select either 'Year' or 'Month'.")

				# Spacing between payments
				spacing_months = total_months // payment_frequency

				# Split rent equally
				equal_amount = round(total_amount / payment_frequency, 2)

				for n in range(payment_frequency):
					payment_date = add_months(start_date, spacing_months * n)

					row = {
						"payment_scheduled_date": payment_date,
						"payment_amount": equal_amount
					}

					if i.is_taxable and i.item_tax_template:
						row["item_tax_template"] = i.item_tax_template
						row["is_taxable"] = 1

					self.append("payment_schedule", row)
	
	
	

		 

	for i in self.schedule_payments:
		end_num = i.number_of_period
		if i.period_type == 'Year':
			end_num = i.number_of_period * 12
			days = i.number_of_period * 365
			i.period_end_date =  frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)
		elif i.period_type=='Month':
			i.period_end_date = frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)

	# if not self.payment_schedule:
	# 	for i in self.schedule_payments:
	# 		end_num = i.number_of_period
	# 		if i.period_type == 'Year':
	# 			end_num = i.number_of_period * 12
	# 			days = i.number_of_period * 365
	# 			i.period_end_date =  frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)
	# 		elif i.period_type=='Month':
	# 			i.period_end_date = frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)
	# 		# doc.payment_schedule = []
	# 		total_amount = self.yearly_rent
	# 		period = end_num
	# 		n = 0
	# 		if i.payment_frequency == '1 Payment':
	# 			total_amount = self.yearly_rent
	# 			n = 1
	# 			period = int(end_num / 12)
	# 		elif i.payment_frequency == '4 Payment':
	# 			total_amount = self.yearly_rent / 4
	# 			n = 1
	# 			period = int(end_num / 3)
	# 		elif i.payment_frequency == '2 Payment':
	# 			total_amount = self.yearly_rent / 2
	# 			n = 1
	# 			period = int(end_num/ 6)
	# 		elif i.payment_frequency == '6 Payment':
	# 			total_amount = self.yearly_rent / 6
	# 			n = 1
	# 			period = int(end_num/ 2)
	# 		elif i.payment_frequency == '3 Payment':
	# 			total_amount = self.yearly_rent / 3
	# 			n = 1
	# 			period = int(end_num/ 4)
	# 		else:
	# 			total_amount = self.yearly_rent/12
	# 			n = 1

	# 		if int(period) > 0:
	# 			for x in range(period):
	# 				row = {
	# 						"payment_scheduled_date": frappe.utils.add_months(i.period_start_date, n-1),
	# 						"payment_amount": total_amount,
	# 					}

	# 				if i.is_taxable and i.item_tax_template:
	# 					row["item_tax_template"] = i.item_tax_template
	# 					row['is_taxable'] = 1

	# 				self.append("payment_schedule", row)

	# 				if i.payment_frequency == '1 Payment':
	# 					n = n + 12
	# 				elif i.payment_frequency == '12 Payment':
	# 					n = n+1
	# 				elif i.payment_frequency == '4 Payment':
	# 					n = n+3
	# 				elif i.payment_frequency == '6 Payment':
	# 					n = n+2
	# 				elif i.payment_frequency == '3 Payment':
	# 					n = n+4
	# 				else:
	# 					n = n+6

		
		
			
# ----------- creating single sales invoice based on TC -------------------
import json
def create_sigl_sales_invoice(self):
	period_end_date = ''
	for i in self.schedule_payments:
		period_end_date = i.period_end_date

	vat = frappe.db.get_value('Sales Taxes and Charges Template',
								{'company': self.company, 'is_default': 1}, 'name')

	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.update({
		"customer": self.name_of_tenant,
		"set_posting_time": 1,
		"posting_date": self.issue_date,
		"due_date": period_end_date,
		"property": self.property_name,
		#"unit": self.unit_number,
		"cost_center": self.cost_center,
		"custom_tenancy_contract": self.name,
	})

	for i in self.payment_schedule:
		sales_invoice.append("items", {
			#"item_code": self.unit_number,
			"qty": 1,
			"rate": i.payment_amount,
			"property": self.property_name,
			"unit": self.unit_number,
			"enable_deferred_revenue": 1,
			"service_start_date": i.service_start_date,
			"description":i.description,
			"service_end_date": i.service_end_date,
			"income_account": i.income_account,
			"item_tax_template": i.item_tax_template,
		})
		frappe.db.set_value("TC Payment Schedule", i.name, "is_accrued", 1)

	for j in self.type_of_charges:
		sales_invoice.append("items", {
			"item_code": self.unit_number,
			"qty": 1,
			"description": j.particulars,
			"rate": j.amount,
			"property": self.property_name,
			#"unit": self.unit_number,
			"income_account": j.account,
			"item_tax_template": j.item_tax_template,
			"description":j.description,
		})
		frappe.db.set_value("Type Of Charges", j.name, "is_accrued", 1)

	# Custom logic to only apply tax if item_tax_template is set
	item_tax_detail = {}
	for item in sales_invoice.items:
		if item.item_tax_template:
			template = frappe.get_doc("Item Tax Template", item.item_tax_template)
			for t in template.taxes:
				account = t.tax_type
				rate = t.tax_rate
				amount = item.rate * item.qty * rate / 100
				if account not in item_tax_detail:
					item_tax_detail[account] = {}
				item_tax_detail[account][item.item_code] = [rate, amount]

	if item_tax_detail:
		sales_invoice.item_wise_tax_detail = json.dumps(item_tax_detail)
		for acc, vals in item_tax_detail.items():
			tax_row = sales_invoice.append("taxes", {})
			tax_row.charge_type = "On Net Total"
			tax_row.account_head = acc
			tax_row.description = f"Tax for {acc}"
			tax_row.tax_amount = sum([v[1] for v in vals.values()])

	sales_invoice.save()
	sales_invoice.submit()

	# Set links to invoice
	for i in self.payment_schedule:
		frappe.db.set_value("TC Payment Schedule", i.name, "sales_invoice", sales_invoice.name)
	for j in self.type_of_charges:
		frappe.db.set_value("Type Of Charges", j.name, "sales_invoice", sales_invoice.name)

	frappe.db.set_value(self.doctype, self.name, 'grand_total', sales_invoice.grand_total)
	frappe.db.set_value(self.doctype, self.name, 'total_taxes_and_charges', sales_invoice.total_taxes_and_charges)
	frappe.db.commit()
	return sales_invoice.name


from frappe.utils import flt

def calculate_schedule_tax(self):
	total_tax = 0.0

	for row in self.payment_schedule:
		if row.item_tax_template:
			tax_template = frappe.get_doc("Item Tax Template", row.item_tax_template)
			for tax in tax_template.taxes:
				rate = flt(tax.tax_rate)
				tax_amount = flt(row.payment_amount * rate / 100)
				total_tax += tax_amount

	for charge in self.type_of_charges:
		if charge.is_taxable and charge.item_tax_template:
			tax_template = frappe.get_doc("Item Tax Template", charge.item_tax_template)
			for tax in tax_template.taxes:
				rate = flt(tax.tax_rate)
				tax_amount = flt(charge.amount * rate / 100)
				total_tax += tax_amount

	self.total_taxes_and_charges = total_tax

	self.grand_total = self.total + total_tax if self.total else 0



# ---------------- function disable ----------------
@frappe.whitelist()
def create_sales_invoice():
	posting_date = nowdate
	payment_schedule = frappe.db.sql('''
		SELECT
			pc.parent,
			tc.name as name,pc.payment_amount,pc.name as pc_name,
			pc.payment_scheduled_date as payment_scheduled_date,
			tc.name_of_tenant as name_of_tenant,pc.service_end_date as service_end_date,
			tc.unit_number,tc.property_name
		FROM
			`tabTC Payment Schedule` as pc
		LEFT JOIN
			`tabTenancy Contract` as tc OdisscussN pc.parent = tc.name
		WHERE
			pc.is_accrued = 0 
			AND pc.docstatus = 1 
			AND pc.parenttype = "Tenancy Contract" ''', as_dict=1)

	tc_name = set()
	for i in payment_schedule:
		tc_name.add(i.parent)

	for i in tc_name:
		tc_doc = frappe.get_doc('Tenancy Contract', i)
		# taking only defult tax 
		vat = frappe.db.get_value('Sales Taxes and Charges Template',{'company':tc_doc.company,'is_default':1},'name') 
		for i in tc_doc.payment_schedule:
			if int(i.idx) + 1 < len(tc_doc.payment_schedule):
				next_payment_scheduled_date = tc_doc.payment_schedule[int(i.idx) + 1].payment_scheduled_date
			else:
				next_payment_scheduled_date = frappe.db.get_value("TA Payment Schedule",{"parent":tc_doc.name},"period_end_date")
			# to check the now date and schedule date 
			if str(i.payment_scheduled_date) == str(posting_date):
				if i.idx  == 1 and i.is_accrued ==0 :
					create_si_idx(i, vat, tc_doc, next_payment_scheduled_date)

				elif i.is_accrued == 0 and i.idx  != 1:
					sales_invoice = frappe.get_doc({
					"doctype": "Sales Invoice",
					"customer": tc_doc.name_of_tenant,
					"set_posting_time":1,
					"posting_date": i.payment_scheduled_date,
					"due_date": i.payment_scheduled_date if str(i.payment_scheduled_date) <= str(posting_date) else str(posting_date),
					"property": tc_doc.property_name,
					"unit": tc_doc.unit_number,
					"custom_tenancy_contract": tc_doc.name,
					# 'taxes_and_charges': vat,
					"items": [
						{
							"item_code": tc_doc.unit_number,
							"qty": 1,
							"rate": i.payment_amount,
							"property": tc_doc.property_name,
							"unit": tc_doc.unit_number,
							"enable_deferred_revenue": 1,
							"service_start_date": i.payment_scheduled_date,
							"service_end_date": next_payment_scheduled_date  # Use next payment date or period_end_date
								}
							]
						})
					sales_invoice.insert()
					sales_invoice.submit()
					frappe.db.set_value("TC Payment Schedule", i.name, "is_accrued", 1)
					frappe.db.set_value("TC Payment Schedule", i.name, "sales_invoice", sales_invoice.name)

	#  ------------------     ------------------------------------- 




def create_si_idx(i, vat, tc_doc, next_payment_scheduled_date):
	posting_date = nowdate()

	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.update({
		"customer": tc_doc.name_of_tenant,
		"set_posting_time": 1,
		"posting_date": i.payment_scheduled_date,
		"due_date": i.payment_scheduled_date if str(i.payment_scheduled_date) <= str(posting_date) else str(posting_date),
		"property": tc_doc.property_name,
		"unit": tc_doc.unit_number,
		"custom_tenancy_contract": tc_doc.name,
		"taxes_and_charges": vat
	})
	sales_invoice.append("items", {
		"item_code": tc_doc.unit_number,
		"qty": 1,
		"rate": i.payment_amount,
		"property": tc_doc.property_name,
		"unit": tc_doc.unit_number,
		"enable_deferred_revenue": 1,
		"service_start_date": i.payment_scheduled_date,
		"service_end_date": next_payment_scheduled_date
	})

	# as per requirement in 1st index need to add the type of charges
	for j in tc_doc.type_of_charges:
		sales_invoice.append("items", {
			"item_code": tc_doc.unit_number,
			"qty": 1,
			"description": j.particulars,
			"rate": j.amount,
			"property": tc_doc.property_name,
			"unit": tc_doc.unit_number
		})
		frappe.db.set_value("Type Of Charges", i.name, "is_accrued", 1)
		frappe.db.set_value("Type Of Charges", i.name, "sales_invoice", sales_invoice.name)

	sales_invoice.insert()
	sales_invoice.submit()

	frappe.db.set_value("TC Payment Schedule", i.name, "is_accrued", 1)
	frappe.db.set_value("TC Payment Schedule", i.name, "sales_invoice", sales_invoice.name)


@frappe.whitelist()
def create_condition_inspection(source_name, target_doc=None):
	if source_name:
		def set_missing_values(source, target):
			target.run_method("set_missing_values")

		doclist = get_mapped_doc("Tenancy Contract", source_name, {
			"Tenancy Contract": {
				"doctype": "Condition Inspection",
				"field_map": {
					"name_of_tenant": "customer",
					"property_name": "property",
					"unit_number": "unit"
				}
			},
			"Condition Inspection Reading": {
				"doctype": "Condition Inspection Reading"
			}
		}, target_doc, set_missing_values)

		doclist.inspection_type = "Move-Out"
		return doclist


@frappe.whitelist()
def renew_tenancy_contract(source_name, target_doc=None):
	if source_name:
		def set_missing_values(source, target):
			target.new_renewal_lease = "Renewal"
			target.condition_inspection = []
			target.schedule_payments = []
			target.payment_schedule = []
			target.append("schedule_payments", {
				"period_start_date": source.schedule_payments[0].period_end_date + timedelta(days=1),
				"period_type": source.schedule_payments[0].period_type,
				"number_of_period": source.schedule_payments[0].number_of_period,
				"payment_frequency": source.schedule_payments[0].payment_frequency
			})

		doclist = get_mapped_doc("Tenancy Contract", source_name, {
			"Tenancy Contract": {
				"doctype": "Tenancy Contract"
			}
		}, target_doc, set_missing_values)
		return doclist


@frappe.whitelist()
def create_quotation(source_name, target_doc=None):
	if source_name:
		def set_missing_values(source, target):
			target.append("items", {
				"item_code": source.unit_number,
				"item_name": source.unit_number,
				"qty": 1,
				"custom_current_rate": source.yearly_rent,
				"uom": "Nos"
			})

		doclist = get_mapped_doc("Tenancy Contract", source_name, {
			"Tenancy Contract": {
				"doctype": "Quotation",
				"field_map": {
					"name_of_tenant": "party_name"
				}
			}
		}, target_doc, set_missing_values)
		return doclist


def creating_post_date_cheque(name):
	tc_doc = frappe.get_doc('Tenancy Contract', name)
	for i in tc_doc.payment_schedule:
		if i.is_pdc == 1:
			bk_acc = frappe.db.get_value('Bank Account', {'name': i.bank_account}, 'account')
			pdc = frappe.get_doc({
				"doctype": "Post Dated Cheque",
				"party_type": "Customer",
				"party": tc_doc.name_of_tenant,
				"posting_date": i.payment_date,
				"bank": i.bank,
				"bank_account": bk_acc,
				"cheque_amount": i.amount,
				"cheque__no": i.payment_date,
				"cheque_date": i.reference_date,
				"tenancy_contract": tc_doc.name,
				"status": "Received",
				"unit": tc_doc.unit_number,
				"property": tc_doc.property_name,
				"amount_in_words": frappe.utils.money_in_words(i.amount),
				"date_of_issue": i.reference_date,
				"expiry_date": i.cheque_end_date,
				"reference": i.name
			})
			pdc.append("cheque_audit_trail", {
				"transaction_date": i.payment_date,
				"status": "Received",
				"remarks": "Cheque Received"
			})
			pdc.insert()
			pdc.submit()
			frappe.db.set_value("TC Payment Schedule", i.name, "pdc", pdc.name)

