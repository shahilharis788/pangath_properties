import frappe
from frappe import ValidationError, _, qb
from frappe.utils.data import flt, fmt_money, getdate, nowdate

import erpnext
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	PaymentEntry,
	get_outstanding_on_journal_entry,
	split_invoices_based_on_payment_terms,
	get_negative_outstanding_invoices,
	get_orders_to_be_billed,
)

from erpnext.accounts.utils import (
	get_account_currency,
	get_outstanding_invoices,
)

from erpnext.controllers.accounts_controller import get_supplier_block_status
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_dimensions
import json

def on_submit(doc, method):
	if doc.tenant_onboarding:
		for i in doc.references:
			if i.reference_doctype == "Journal Entry":
				frappe.db.set_value("Journal Entry", i.reference_name, "pe_created", 1)
				frappe.db.set_value(
					"Journal Entry", i.reference_name, "payment_entry", doc.name
				)
				doc.db_set("journal_entry", i.reference_name)

			to_doc = frappe.get_doc("Tenant Onboarding", doc.tenant_onboarding)
			for schedule in to_doc.payment_schedule:
				if schedule.journal_entry == i.reference_name:
					frappe.db.set_value(
						schedule.doctype, schedule.name, "payment_entry_created", 1
					)
					frappe.db.set_value(
						schedule.doctype, schedule.name, "payment_entry", doc.name
					)
	if doc.custom_booking_agreement_reference:

        	frappe.db.set_value(
            "Lease Agreement",
            doc.custom_booking_agreement_reference,
            "payment_entry_reference",
            doc.name
        )




def before_submit(doc,method):
	for i in doc.references:
		if i.reference_doctype == "Sales Invoice":
			doc.custom_tenancy_contract = frappe.db.get_value("Sales Invoice",i.reference_name,"custom_tenancy_contract")


def on_cancel(doc, method):
	if doc.tenant_onboarding:
		for i in doc.references:
			if i.reference_doctype == "Journal Entry":
				frappe.db.set_value("Journal Entry", i.reference_name, "pe_created", 0)
				frappe.db.set_value(
					"Journal Entry", i.reference_name, "payment_entry", ""
				)
				doc.db_set("journal_entry", "")

			to_doc = frappe.get_doc("Tenant Onboarding", doc.tenant_onboarding)
			for schedule in to_doc.payment_schedule:
				if schedule.journal_entry == i.reference_name:
					frappe.db.set_value(
						schedule.doctype, schedule.name, "payment_entry_created", 0
					)
					frappe.db.set_value(
						schedule.doctype, schedule.name, "payment_entry", ""
					)

		tob_doc = frappe.get_doc("Tenant Onboarding", doc.tenant_onboarding)
		if tob_doc.type_of_charges:
			for m in tob_doc.type_of_charges:
				if m.payment_entry == doc.name:
					frappe.db.set_value(m.doctype, m.name, "payment_entry_created", 0)
					frappe.db.set_value(m.doctype, m.name, "payment_entry", "")


class InvalidPaymentEntry(ValidationError):
	pass


class CustomPaymentEntry(PaymentEntry):
	def get_valid_reference_doctypes(self):
		if self.party_type == "Customer":
			return (
				"Sales Order",
				"Sales Invoice",
				"Journal Entry",
				"Dunning",
				"Tenant Onboarding Termination",
			)
		elif self.party_type == "Supplier":
			return ("Purchase Order", "Purchase Invoice", "Journal Entry")
		elif self.party_type == "Shareholder":
			return ("Journal Entry",)
		elif self.party_type == "Employee":
			return ("Journal Entry",)

	def validate_payment_against_negative_invoice(self):
		if (self.payment_type != "Pay" or self.party_type != "Customer") and (
			self.payment_type != "Receive" or self.party_type != "Supplier"
		):
			return

		total_negative_outstanding = flt(
			sum(
				abs(flt(d.outstanding_amount))
				for d in self.get("references")
				if flt(d.outstanding_amount) < 0
			),
			self.references[0].precision("outstanding_amount")
			if self.references
			else None,
		)

		paid_amount = (
			self.paid_amount if self.payment_type == "Receive" else self.received_amount
		)
		additional_charges = sum(flt(d.amount) for d in self.deductions)

		if not total_negative_outstanding:
			if self.party_type == "Supplier":
				msg = _(
					"Cannot receive from Supplier without any negative outstanding invoice"
				)

				frappe.throw(msg, InvalidPaymentEntry)

		elif paid_amount - additional_charges > total_negative_outstanding:
			frappe.throw(
				_(
					"Paid Amount cannot be greater than total negative outstanding amount {0}"
				).format(fmt_money(total_negative_outstanding)),
				InvalidPaymentEntry,
			)

	def set_missing_ref_details(
		self, force: bool = False, update_ref_details_only_for: list | None = None,
		ref_exchange_rate: float | None = None,
	) -> None:
		for d in self.get("references"):
			if d.allocated_amount:
				if update_ref_details_only_for and (
					not (d.reference_doctype, d.reference_name)
					in update_ref_details_only_for
				):
					continue
				ref_details = get_reference_details(
					d.reference_doctype, d.reference_name, self.party_account_currency
				)
				if ref_exchange_rate and d.reference_doctype == "Journal Entry":
					ref_details.update({"exchange_rate": ref_exchange_rate})

				for field, value in ref_details.items():
					if d.exchange_gain_loss:
						# for cases where gain/loss is booked into invoice
						# exchange_gain_loss is calculated from invoice & populated
						# and row.exchange_rate is already set to payment entry's exchange rate
						# refer -> `update_reference_in_payment_entry()` in utils.py
						continue

					if field == "exchange_rate" or not d.get(field) or force:
						d.db_set(field, value)

	def validate_allocated_amount_with_latest_data(self):
		if self.references:
			uniq_vouchers = set([(x.reference_doctype, x.reference_name) for x in self.references])
			vouchers = [frappe._dict({"voucher_type": x[0], "voucher_no": x[1]}) for x in uniq_vouchers]
			latest_references = get_outstanding_reference_documents(
				{
					"posting_date": self.posting_date,
					"company": self.company,
					"party_type": self.party_type,
					"payment_type": self.payment_type,
					"party": self.party,
					"party_account": self.paid_from if self.payment_type == "Receive" else self.paid_to,
					"get_outstanding_invoices": True,
					"get_orders_to_be_billed": True,
					"vouchers": vouchers,
					"book_advance_payments_in_separate_party_account": self.book_advance_payments_in_separate_party_account,
				},
				validate=True,
			)

			# Group latest_references by (voucher_type, voucher_no)
			latest_lookup = {}
			for d in latest_references:
				d = frappe._dict(d)
				latest_lookup.setdefault((d.voucher_type, d.voucher_no), frappe._dict())[d.payment_term] = d

			for idx, d in enumerate(self.get("references"), start=1):
				latest = latest_lookup.get((d.reference_doctype, d.reference_name)) or frappe._dict()

				# If term based allocation is enabled, throw
				if (
					d.payment_term is None or d.payment_term == ""
				) and self.term_based_allocation_enabled_for_reference(
					d.reference_doctype, d.reference_name
				):
					frappe.throw(
						_(
							"{0} has Payment Term based allocation enabled. Select a Payment Term for Row #{1} in Payment References section"
						).format(frappe.bold(d.reference_name), frappe.bold(idx))
					)

				# if no payment template is used by invoice and has a custom term(no `payment_term`), then invoice outstanding will be in 'None' key
				latest = latest.get(d.payment_term) or latest.get(None)
				# The reference has already been fully paid
				if not latest:
					frappe.throw(
						_("{0} {1} has already been fully paid.").format(_(d.reference_doctype), d.reference_name)
					)
				# The reference has already been partly paid
				elif (
					latest.outstanding_amount < latest.invoice_amount
					and flt(d.outstanding_amount, d.precision("outstanding_amount"))
					!= flt(latest.outstanding_amount, d.precision("outstanding_amount"))
					and d.payment_term == ""
				):
					frappe.throw(
						_(
							"{0} {1} has already been partly paid. Please use the 'Get Outstanding Invoice' or the 'Get Outstanding Orders' button to get the latest outstanding amounts."
						).format(_(d.reference_doctype), d.reference_name)
					)

				fail_message = _("Row #{0}: Allocated Amount cannot be greater than outstanding amount.")

				if (
					d.payment_term
					and (
						(flt(d.allocated_amount)) > 0
						and latest.payment_term_outstanding
						and (flt(d.allocated_amount) > flt(latest.payment_term_outstanding))
					)
					and self.term_based_allocation_enabled_for_reference(d.reference_doctype, d.reference_name)
				):
					frappe.throw(
						_(
							"Row #{0}: Allocated amount:{1} is greater than outstanding amount:{2} for Payment Term {3}"
						).format(
							d.idx, d.allocated_amount, latest.payment_term_outstanding, d.payment_term
						)
					)

				if (flt(d.allocated_amount)) > 0 and flt(d.allocated_amount) > flt(latest.outstanding_amount):
					frappe.throw(fail_message.format(d.idx))

				# Check for negative outstanding invoices as well
				if flt(d.allocated_amount) < 0 and flt(d.allocated_amount) < flt(latest.outstanding_amount):
					frappe.throw(fail_message.format(d.idx))


	def add_party_gl_entries(self, gl_entries):
		if self.party_account:
			if self.payment_type == "Receive":
				against_account = self.paid_to
			else:
				against_account = self.paid_from

			party_gl_dict = self.get_gl_dict(
				{
					"account": self.party_account,
					"party_type": self.party_type,
					"party": self.party,
					"against": against_account,
					"account_currency": self.party_account_currency,
					"cost_center": self.cost_center,
				},
				item=self,
			)

			dr_or_cr = (
				"credit"
				if erpnext.get_party_account_type(self.party_type) == "Receivable"
				else "debit"
			)

			if self.tenant_onboarding_termination and dr_or_cr != "debit":
				dr_or_cr = "debit"

			for d in self.get("references"):
				cost_center = self.cost_center
				if d.reference_doctype == "Sales Invoice" and not cost_center:
					cost_center = frappe.db.get_value(
						d.reference_doctype, d.reference_name, "cost_center"
					)
				gle = party_gl_dict.copy()
				gle.update(
					{
						"against_voucher_type": d.reference_doctype,
						"against_voucher": d.reference_name,
						"cost_center": cost_center,
					}
				)

				allocated_amount_in_company_currency = (
					self.calculate_base_allocated_amount_for_reference(d)
				)

				gle.update(
					{
						dr_or_cr + "_in_account_currency": d.allocated_amount,
						dr_or_cr: allocated_amount_in_company_currency,
					}
				)

				gl_entries.append(gle)

			if self.unallocated_amount:
				exchange_rate = self.get_exchange_rate()
				base_unallocated_amount = self.unallocated_amount * exchange_rate

				gle = party_gl_dict.copy()

				gle.update(
					{
						dr_or_cr + "_in_account_currency": self.unallocated_amount,
						dr_or_cr: base_unallocated_amount,
					}
				)

				gl_entries.append(gle)


def get_outstanding_reference_documents(args, validate=False):
	if isinstance(args, str):
		args = json.loads(args)

	if args.get("party_type") == "Member":
		return

	if not args.get("get_outstanding_invoices") and not args.get("get_orders_to_be_billed"):
		args["get_outstanding_invoices"] = True

	ple = qb.DocType("Payment Ledger Entry")
	common_filter = []
	accounting_dimensions_filter = []
	posting_and_due_date = []

	# confirm that Supplier is not blocked
	if args.get("party_type") == "Supplier":
		supplier_status = get_supplier_block_status(args["party"])
		if supplier_status["on_hold"]:
			if supplier_status["hold_type"] == "All":
				return []
			elif supplier_status["hold_type"] == "Payments":
				if (
					not supplier_status["release_date"] or getdate(nowdate()) <= supplier_status["release_date"]
				):
					return []

	party_account_currency = get_account_currency(args.get("party_account"))
	company_currency = frappe.get_cached_value("Company", args.get("company"), "default_currency")

	# Get positive outstanding sales /purchase invoices
	condition = ""
	if args.get("voucher_type") and args.get("voucher_no"):
		condition = " and voucher_type={0} and voucher_no={1}".format(
			frappe.db.escape(args["voucher_type"]), frappe.db.escape(args["voucher_no"])
		)
		common_filter.append(ple.voucher_type == args["voucher_type"])
		common_filter.append(ple.voucher_no == args["voucher_no"])

	# Add cost center condition
	if args.get("cost_center"):
		condition += " and cost_center='%s'" % args.get("cost_center")
		accounting_dimensions_filter.append(ple.cost_center == args.get("cost_center"))

	# dynamic dimension filters
	active_dimensions = get_dimensions()[0]
	for dim in active_dimensions:
		if args.get(dim.fieldname):
			condition += " and {0}='{1}'".format(dim.fieldname, args.get(dim.fieldname))
			accounting_dimensions_filter.append(ple[dim.fieldname] == args.get(dim.fieldname))

	date_fields_dict = {
		"posting_date": ["from_posting_date", "to_posting_date"],
		"due_date": ["from_due_date", "to_due_date"],
	}

	for fieldname, date_fields in date_fields_dict.items():
		if args.get(date_fields[0]) and args.get(date_fields[1]):
			condition += " and {0} between '{1}' and '{2}'".format(
				fieldname, args.get(date_fields[0]), args.get(date_fields[1])
			)
			posting_and_due_date.append(ple[fieldname][args.get(date_fields[0]) : args.get(date_fields[1])])
		elif args.get(date_fields[0]):
			# if only from date is supplied
			condition += " and {0} >= '{1}'".format(fieldname, args.get(date_fields[0]))
			posting_and_due_date.append(ple[fieldname].gte(args.get(date_fields[0])))
		elif args.get(date_fields[1]):
			# if only to date is supplied
			condition += " and {0} <= '{1}'".format(fieldname, args.get(date_fields[1]))
			posting_and_due_date.append(ple[fieldname].lte(args.get(date_fields[1])))

	if args.get("company"):
		condition += " and company = {0}".format(frappe.db.escape(args.get("company")))
		common_filter.append(ple.company == args.get("company"))

	outstanding_invoices = []
	negative_outstanding_invoices = []

	if args.get("book_advance_payments_in_separate_party_account"):
		party_account = get_party_account(args.get("party_type"), args.get("party"), args.get("company"))
	else:
		party_account = args.get("party_account")

	if args.get("get_outstanding_invoices"):
		outstanding_invoices = get_outstanding_invoices(
			args.get("party_type"),
			args.get("party"),
			[party_account],
			common_filter=common_filter,
			posting_date=posting_and_due_date,
			min_outstanding=args.get("outstanding_amt_greater_than"),
			max_outstanding=args.get("outstanding_amt_less_than"),
			accounting_dimensions=accounting_dimensions_filter,
			vouchers=args.get("vouchers") or None,
		)

		outstanding_invoices = split_invoices_based_on_payment_terms(
			outstanding_invoices, args.get("company")
		)

		for d in outstanding_invoices:
			d["exchange_rate"] = 1
			if party_account_currency != company_currency:
				if d.voucher_type in frappe.get_hooks("invoice_doctypes"):
					d["exchange_rate"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "conversion_rate")
				elif d.voucher_type == "Journal Entry":
					d["exchange_rate"] = get_exchange_rate(
						party_account_currency, company_currency, d.posting_date
					)
			if d.voucher_type in ("Purchase Invoice"):
				d["bill_no"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "bill_no")

		# Get negative outstanding sales /purchase invoices
		if args.get("party_type") != "Employee" and not args.get("voucher_no"):
			negative_outstanding_invoices = get_negative_outstanding_invoices(
				args.get("party_type"),
				args.get("party"),
				args.get("party_account"),
				party_account_currency,
				company_currency,
				condition=condition,
			)

	# Get all SO / PO which are not fully billed or against which full advance not paid
	orders_to_be_billed = []
	if args.get("get_orders_to_be_billed"):
		orders_to_be_billed = get_orders_to_be_billed(
			args.get("posting_date"),
			args.get("party_type"),
			args.get("party"),
			args.get("company"),
			party_account_currency,
			company_currency,
			filters=args,
		)

	data = negative_outstanding_invoices + outstanding_invoices + orders_to_be_billed

	if not data:
		if args.get("get_outstanding_invoices") and args.get("get_orders_to_be_billed"):
			ref_document_type = "invoices or orders"
		elif args.get("get_outstanding_invoices"):
			ref_document_type = "invoices"
		elif args.get("get_orders_to_be_billed"):
			ref_document_type = "orders"

		if not validate:
			frappe.msgprint(
				_(
					"No outstanding {0} found for the {1} {2} which qualify the filters you have specified."
				).format(
					_(ref_document_type), _(args.get("party_type")).lower(), frappe.bold(args.get("party"))
				)
			)

	return data



def get_reference_details(reference_doctype, reference_name, party_account_currency):
	total_amount = outstanding_amount = exchange_rate = None

	ref_doc = frappe.get_doc(reference_doctype, reference_name)
	company_currency = ref_doc.get("company_currency") or erpnext.get_company_currency(
		ref_doc.company
	)

	if reference_doctype == "Dunning":
		total_amount = outstanding_amount = ref_doc.get("dunning_amount")
		exchange_rate = 1

	elif reference_doctype == "Journal Entry" and ref_doc.docstatus == 1:
		total_amount = ref_doc.get("total_amount")
		if ref_doc.multi_currency:
			exchange_rate = get_exchange_rate(
				party_account_currency, company_currency, ref_doc.posting_date
			)
		else:
			exchange_rate = 1
			outstanding_amount = get_outstanding_on_journal_entry(reference_name)

	elif reference_doctype != "Journal Entry":
		if not total_amount:
			if party_account_currency == company_currency:
				# for handling cases that don't have multi-currency (base field)
				total_amount = (
					ref_doc.get("base_rounded_total")
					or ref_doc.get("rounded_total")
					or ref_doc.get("base_grand_total")
					or ref_doc.get("grand_total")
					or ref_doc.get("total_refundable")
				)
				exchange_rate = 1
			else:
				total_amount = ref_doc.get("rounded_total") or ref_doc.get(
					"grand_total"
				)
		if not exchange_rate:
			# Get the exchange rate from the original ref doc
			# or get it based on the posting date of the ref doc.
			exchange_rate = ref_doc.get("conversion_rate") or get_exchange_rate(
				party_account_currency, company_currency, ref_doc.posting_date
			)

		if reference_doctype in ("Sales Invoice", "Purchase Invoice"):
			outstanding_amount = ref_doc.get("outstanding_amount")
		elif reference_doctype == "Tenant Onboarding Termination":
			outstanding_amount = ref_doc.get("total_refundable")
		else:
			outstanding_amount = flt(total_amount) - flt(ref_doc.get("advance_paid"))

	else:
		# Get the exchange rate based on the posting date of the ref doc.
		exchange_rate = get_exchange_rate(
			party_account_currency, company_currency, ref_doc.posting_date
		)

	return frappe._dict(
		{
			"due_date": ref_doc.get("due_date"),
			"total_amount": flt(total_amount),
			"outstanding_amount": flt(outstanding_amount),
			"exchange_rate": flt(exchange_rate),
			"bill_no": ref_doc.get("bill_no"),
		}
	)


@frappe.whitelist()
def get_refernce(ref):
	tenancy_contract = frappe.db.get_value("Sales Invoice",ref,"custom_tenancy_contract")
	if tenancy_contract:
		if frappe.db.exists("TC Payment Schedule",{"parent":tenancy_contract,"sales_invoice":ref}):
			return frappe.get_doc("TC Payment Schedule",{"parent":tenancy_contract,"sales_invoice":ref})
		if frappe.db.exists("Type Of Charges",{"parent":tenancy_contract,"sales_invoice":ref}):
			return frappe.get_doc("Type Of Charges",{"parent":tenancy_contract,"sales_invoice":ref})