# Copyright (c) 2025, iterative and contributors
# For license information, please see license.txt


import frappe
import json
from frappe.model.document import Document
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class TenancyApplication(Document):
    def validate(self):
        if self.workflow_state == "Rejected" and not self.remarks:
            frappe.throw(_("Please Enter Remarks"))
        populate_payment_schedule(self)
        total_charges = 0
        for i in self.type_of_charges:
            total_charges += i.amount

        self.total = total_charges + flt(self.yearly_rent)
        
        if not self.is_existing_customer:
            pass
        
        if self.is_existing_customer and self.customer:
            tax_id, terms = frappe.db.get_value("Customer", self.customer, ["tax_id","payment_terms"])
            self.tax_id = tax_id
            self.payment_terms_template = terms
    
    def on_cancel(self):
        self.workflow_state = "Draft"
        frappe.db.set_value("Unit", self.unit, "status", "Available")
        frappe.db.set_value("Unit", self.parking, "status", "Available")

    def before_submit(self):
        # if self.is_existing_customer == 0:
        #     if frappe.db.exists("Customer", {"name": self.tenant_name}):
        #         frappe.throw(f'There is Already a customer named {self.tenant_name}')
        #     customer = frappe.new_doc("Customer")
        #     customer.customer_name = self.tenant_name
        #     customer.custom_passport_no = self.passport_no
        #     customer.custom_contact_no = self.contact_no
        #     customer.email_id = self.email
        #     customer.custom_nationality = self.nationality
        #     customer.custom_emirate_id = self.custom_emirates_id
        #     customer.territory = self.territory,
        #     customer.opportunity_name =  self.opportunity
        #     customer.tax_id = self.tax_id
        #     customer.custom_emirates_id = self.custom_emirates_id
        #     customer.payment_terms = self.payment_terms_template
            
            if self.opportunity:
                opportunity = frappe.get_doc("Opportunity",self.opportunity)
                # frappe.set_value('Opportunity', self.opportunity,'status', 'Tenancy Application')
                if opportunity.opportunity_from == "Lead":
                    customer.lead_name  = opportunity.party_name


            # customer.save()
            # self.db_set("customer",customer.name)
            # frappe.db.set_value("Lead",customer.lead_name,"status","Tenancy Application")

                

            # if self.unit:
            #     doc = frappe.get_doc("Unit", self.unit)
            #     doc.status = "Reservation"
            #     doc.save()

        # update the status if its new or old customer
        # if self.opportunity:
        #     frappe.set_value('Opportunity', self.opportunity,'status', 'Tenancy Application')

@frappe.whitelist()
def create_tenant_onboarding(args):
    args = json.loads(args)
    if not frappe.db.exists("Customer", args.get("tenant_name")):
        frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": args.get("tenant_name"),
                "customer_type": args.get("tenant_type"),
                "customer_group": "Individual",
                "territory": args.get("territory"),
                "mobile_no": args.get("contact_no"),
                "email_id": args.get("email"),
                "property_name": args.get("property"),
                "unit_name": args.get("unit"),
                
            }
        ).insert(ignore_mandatory=True)
    la = frappe.new_doc("Tenant Onboarding")
    la.customer = args.get("tenant_name")
    la.unit = args.get("unit")
    la.building = args.get("property")
    la.tenancy_application = args.get("name")
    la.tenant_type = args.get("tenant_type")
    la.company_name = args.get("company_name")
    la.trade_license_no = args.get("trade_license_no")
    unit_doc = frappe.get_doc("Unit", args.get("unit"))
    for i in unit_doc.type_of_charges:
        la.append(
            "type_of_charges",
            {
                "particulars": i.particulars,
                "refund": i.refund,
                "amount": i.amount,
                "vat_percent": i.vat_percent,
                "tax": i.tax,
            },
        )
    la.insert(ignore_mandatory=True)
    if la:
        return la.name



def populate_payment_schedule(self):
    if not self.payment_details:
        for i in self.payments:
            end_num = i.number_of_period
            if i.period_type == 'Year':
                end_num = i.number_of_period * 12
                days = i.number_of_period * 365
                i.period_end_date =  frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)
            elif i.period_type=='Month':
                i.period_end_date = frappe.utils.add_days(frappe.utils.add_months(i.period_start_date, end_num),-1)

            # doc.payment_schedule = []
            total_amount = self.yearly_rent
            period = end_num
            n = 0
            if i.payment_frequency == '1 Payment':
                total_amount = self.yearly_rent
                n = 1
                period = int(end_num / 12)
            elif i.payment_frequency == '4 Payment':
                total_amount = self.yearly_rent / 4
                n = 1
                period = int(end_num / 3)
            elif i.payment_frequency == '2 Payment':
                total_amount = self.yearly_rent / 2
                n = 1
                period = int(end_num/ 6)
            elif i.payment_frequency == '6 Payment':
                total_amount = self.yearly_rent / 6
                n = 1
                period = int(end_num/ 2)
            elif i.payment_frequency == '3 Payment':
                total_amount = self.yearly_rent / 3
                n = 1
                period = int(end_num/ 4)
            else:
                total_amount = self.yearly_rent/12
                n = 1

            if int(period) > 0:
                for x in range(period):
                    self.append(
                        "payment_details",
                        {
                            "start_date": frappe.utils.add_months(i.period_start_date, n-1),
                            "amount": total_amount,
                        },
                    )
                    if i.payment_frequency == '1 Payment':
                        n = n + 12
                    elif i.payment_frequency == '12 Payment':
                        n = n+1
                    elif i.payment_frequency == '4 Payment':
                        n = n+3
                    elif i.payment_frequency == '6 Payment':
                        n = n+2
                    elif i.payment_frequency == '3 Payment':
                        n = n+4
                    else:
                        n = n+6
@frappe.whitelist()
def create_tenancy_contract(source_name, target_doc=None):
    tenc_cont = frappe.db.get_value("Tenancy Contract", {"proposal_agreement": source_name})
    if tenc_cont:
        frappe.throw(f'Tenancy Contract <b>{tenc_cont}</b> Linked with Proposal Agreement')
    
    if source_name:
        def set_missing_values(source, target):
            target.run_method("set_missing_values")
        doclist = get_mapped_doc("Tenancy Application", source_name, {
            "Tenancy Application": {
                "doctype": "Tenancy Contract",
                "field_map": {
                    "yearly_rent":"yearly_rent",
                    "unit":"unit_number",
                    "monthly_rent":"monthly_rent",
                    'name_of_tenant' :'tenant_name',
                    "customer":"name_of_tenant",
                    "name":"tenancy_application",
                    "opportunity":"opportunity",
                    "name": "proposal_agreement",
                    "tenant_name": "name_of_tenant",
                }
            },
            "TA Payment  Details": {
				"doctype": "TC Payment Schedule",
				"field_map": [
					["start_date","payment_scheduled_date"],
                    [ "amount","payment_amount",]
				],
			},
             "TA Payment Schedule": {
				"doctype": "TA Payment Schedule",
				"field_map": [
					["period_start_date","period_start_date"],
                    [ "period_type","period_type",],
                    ["number_of_period","number_of_period"],
                    ["payment_frequency","payment_frequency"],
                    ["period_end_date","period_end_date"]
				],
			},

        }, target_doc, set_missing_values)
       

        return doclist


@frappe.whitelist()
def create_payment_entry(source_name, target_doc=None):
    if source_name:
        doclist = get_mapped_doc("Tenancy Application", source_name, {
            "Tenancy Application": {
                "doctype": "Payment Entry",
                 "field_map": {
                    "customer":"party",
                    "name":"custom_tenancy_application",
                    "customer_name":"party_name"
                }
            },
        }, target_doc)
        doclist.party_type = "Customer"
        return doclist

@frappe.whitelist()
def create_booking_agreement(source_name, target_doc=None):
    book_agr = frappe.db.get_value("Lease Agreement", {"proposal_agreement": source_name})
    
    if book_agr:
        frappe.throw(f'Proposal already linked to Booking <b>{book_agr}</b>')

    if source_name:
        doclist = get_mapped_doc("Tenancy Application", source_name, {
            "Tenancy Application": {
                "doctype": "Lease Agreement",
                 "field_map": {
                    "customer":"customer",
                    "name":"proposal_agreement",
                }
            },
        }, target_doc)
        
        return doclist 