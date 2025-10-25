import frappe
from frappe import _

def on_cancel(doc, method):
    if doc.tenant_onboarding:
            to_doc = frappe.get_doc('Tenant Onboarding', doc.tenant_onboarding)
            for schedule in  to_doc.payment_schedule:
                if schedule.journal_entry == doc.name:
                    frappe.db.set_value(schedule.doctype, schedule.name, 'journal_entry_created', 0)
                    frappe.db.set_value(schedule.doctype, schedule.name, 'journal_entry', '')

            # if to_doc.type_of_charges:
            #     for m in to_doc.type_of_charges:
            #         if m.journal_entry == doc.name:
            #             frappe.db.set_value(m.doctype, m.name, 'journal_entry_created', 0)
            #             frappe.db.set_value(m.doctype, m.name, 'journal_entry', '')


def validate(doc,method):
    for i in doc.accounts:
        if i.reference_type == "Sales Invoice":
            doc.custom_tenancy_contract = frappe.db.get_value("Sales Invoice",i.reference_name,"custom_tenancy_contract")


@frappe.whitelist()
def get_units_r_proty(data):

    data = frappe.parse_json(data)
    result = []

    for i in data:
        debit_amt = i.get('debit_in_account_currency')
        credit_amt = i.get('credit_in_account_currency')
        if i.get('entry_for') == 'Property':
            unit_list = frappe.db.get_list('Unit', filters={'property': i.get('property')}, fields=['name', 'property'])
            num_units = len(unit_list)
            debit_amount = 0
            credit_amount  =0

            if num_units > 0:
                if debit_amt:
                    debit_amount = debit_amt / num_units
                elif credit_amt:
                    credit_amount = credit_amt / num_units

                for unit in unit_list:
                    entry = i.copy()
                    entry['property'] = unit.get('property')
                    entry['unit'] = unit.get('name')
                    entry['debit_in_account_currency'] = debit_amount
                    entry['credit_in_account_currency'] = credit_amount
                    result.append(entry)
            else:
                # No units found, just append the original entry
                result.append(i)
        elif i.get('entry_for') == 'Unit':
            list_unit = frappe.db.get_list('Unit',{'is_group': 0, 'parent_unit': i.get('unit')}, 'name')
            if list_unit:
                num_units = len(list_unit)
                debit_amount = 0
                credit_amount = 0

                if num_units > 0:
                    if debit_amt:
                        debit_amount = debit_amt / num_units
                    elif credit_amt:
                        credit_amount = credit_amt / num_units
        
                    for unit in list_unit:
                        entry = i.copy()
                        entry['unit'] = unit.get('name')
                        entry['debit_in_account_currency'] = debit_amount
                        entry['credit_in_account_currency'] = credit_amount
                        result.append(entry)
                else:
                    # No units found, just append the original entry
                    result.append(i)


        else:
            result.append(i)
    return result

    