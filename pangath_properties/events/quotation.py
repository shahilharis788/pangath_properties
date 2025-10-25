import frappe
# from frappe.model.mapper import get_mapped_doc
# @frappe.whitelist()
# def create_tenancy_application(source_name, target_doc=None):
#     if source_name:
#         def set_missing_values(source, target):
#             target.is_existing_customer =1
#         doclist = get_mapped_doc("Quotation", source_name, {
#             "Quotation": {
#                 "doctype": "Tenancy Application",
#                 "field_map": {
#                   "party_name":"customer"
#                 }
#             }
#         }, target_doc, set_missing_values)
#         return doclist
