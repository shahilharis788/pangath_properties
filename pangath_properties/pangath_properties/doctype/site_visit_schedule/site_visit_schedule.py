# Copyright (c) 2024, iterative and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SiteVisitSchedule(Document):
  pass


@frappe.whitelist()
def create_site_visit_feedback(source_name, target_doc=None):
  if(source_name):
    doclist = get_mapped_doc("Site Visit Schedule", source_name, {
      "Site Visit Schedule":{
        "doctype":"Visitor Feedback",
        "field_map":{
          "date_of_visiting":"date_of_visit",
          "visitors_full_name":"visitors__full_name",
          "name":"site_visit_schedule"
        },
        # "postprocess":update
      },
    }, target_doc)
    return doclist
