# Copyright (c) 2022, iterative and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet
from frappe import _

class Property(NestedSet):
	nsm_parent_field = "parent_unit"

	def on_update(self):
		self.update_nsm_model()

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	pass
	def after_insert(self):
		insert_dashboards(self)

@frappe.whitelist()
def fetch_unit_details(name):
	property = frappe.form_dict.name
	query = '''
		select
			count(u.name) as unit_number,
			count(CASE WHEN u.status='Rented' THEN 1 END) as rented_units,
			count(CASE WHEN u.status='Leased' THEN 1 END) as leased_units,
			count(CASE WHEN u.status='Sold' THEN 1 END) as sold_units,
			count(CASE WHEN u.status='Available' THEN 1 END) as available_units,
			sum(u.rent) as amount,
			sum(u.purchase_price) as purchase_price
		FROM
			`tabUnit` as u LEFT JOIN
			`tabProperty` as b ON u.property=b.name
		WHERE'''
	query =  f"{query} property={json.dumps(property)}"
	# query =  f"{query} GROUP BY u.name"
	data = frappe.db.sql(f"{query}", as_dict=True)
	frappe.response['data'] = data

def insert_dashboards(self):
	card_data = [
		{
			"doctype": "Number Card",
			"name": self.building_name + " Total Units",
			"label": self.building_name + " Total Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([["Unit", "property", "=", self.name]]),
			"dynamic_filters_json": "[]"
		},
		{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Rented Total Units",
			"label": self.building_name + " Residential-Rented Total Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"]
			]),
			"dynamic_filters_json": "[]"
		},
		{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Total Units",
			"label": self.building_name + " Residential-Sale Total Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"]
			]),
			"dynamic_filters_json": "[]"
		},
		{
			"doctype": "Number Card",
			"name": self.building_name + " Commercial Total Units",
			"label": self.building_name + " Commercial Total Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"]
			]),
			"dynamic_filters_json": "[]"
		},
		{
			"doctype": "Number Card",
			"name": self.building_name + " Parking Total Units",
			"label": self.building_name + " Parking Total Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"]
			]),
			"dynamic_filters_json": "[]"
		},
		{
			"doctype": "Number Card",
			"name": self.building_name + " Available Units",
			"label": self.building_name + " Available Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "status", "=", "Available"]
			]),
			"dynamic_filters_json": "[]"
		},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Rented Available Units",
			"label": self.building_name + " Residential-Rented Available Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"],
				["Unit", "status", "=", "Available"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Available Units",
			"label": self.building_name + " Residential-Sale Available Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"],
				["Unit", "status", "=", "Available"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Commercial Available Units",
			"label": self.building_name + " Commercial Available Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"],
				["Unit", "status", "=", "Available"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Parking Available Units",
			"label": self.building_name + " Parking Available Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"],
				["Unit", "status", "=", "Available"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Booked Units",
			"label": self.building_name + " Booked Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "status", "=", "Booked"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Rented Booked Units",
			"label": self.building_name + " Residential-Rented Booked Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"],
				["Unit", "status", "=", "Booked"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Booked Units",
			"label": self.building_name + " Residential-Sale Booked Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"],
				["Unit", "status", "=", "Booked"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Commercial Booked Units",
			"label": self.building_name + " Commercial Booked Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"],
				["Unit", "status", "=", "Booked"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Parking Booked Units",
			"label": self.building_name + " Parking Booked Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Daily",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"],
				["Unit", "status", "=", "Booked"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Leased Units",
			"label": self.building_name + " Leased Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "status", "=", "Leased"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Rented Leased Units",
			"label": self.building_name + " Residential-Rented Leased Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"],
				["Unit", "status", "=", "Leased"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Leased Units",
			"label": self.building_name + " Residential-Sale Leased Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"],
				["Unit", "status", "=", "Leased"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Commercial Leased Units",
			"label": self.building_name + " Commercial Leased Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"],
				["Unit", "status", "=", "Leased"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Parking Leased Units",
			"label": self.building_name + " Parking Leased Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"],
				["Unit", "status", "=", "Leased"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Sold Units",
			"label": self.building_name + " Sold Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "status", "=", "Sold"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential - Rented Sold Units",
			"label": self.building_name + " Residential - Rented Sold Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"],
				["Unit", "status", "=", "Sold"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Sold Units",
			"label": self.building_name + " Residential-Sale Sold Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"],
				["Unit", "status", "=", "Sold"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Commercial Sold Units",
			"label": self.building_name + " Commercial Sold Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"],
				["Unit", "status", "=", "Sold"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Parking Sold Units",
			"label": self.building_name + " Parking Sold Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"],
				["Unit", "status", "=", "Sold"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Not Hand Over Units",
			"label": self.building_name + " Not Hand Over Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "status", "=", "Not Hand Over"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Rented Not Handed Over Units",
			"label": self.building_name + " Residential-Rented Not Handed Over Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Rental"],
				["Unit", "status", "=", "Not Hand Over"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name": self.building_name + " Residential-Sale Not Hand Over Units",
			"label": self.building_name + " Residential-Sale Not Hand Over Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Residential - Sale"],
				["Unit", "status", "=", "Not Hand Over"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name":self.building_name + " Commercial Not Hand Over Units",
			"label":self.building_name + " Commercial Not Hand Over Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Commercial"],
				["Unit", "status", "=", "Not Hand Over"]
			]),
			"dynamic_filters_json": "[]"
			},
			{
			"doctype": "Number Card",
			"name":self.building_name + " Parking Not Hand Over Units",
			"label":self.building_name + " Parking Not Hand Over Units",
			"type": "Document Type",
			"function": "Count",
			"document_type": "Unit",
			"report_function": "Sum",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Unit", "property", "=", self.name],
				["Unit", "unit_nature", "=", "Parking"],
				["Unit", "status", "=", "Not Hand Over"]
			]),
			"dynamic_filters_json": "[]"
			}
				]
	for card in card_data:
		new_card = frappe.get_doc(card)
		new_card.insert()
	new_chart = frappe.get_doc({
		"doctype": "Dashboard Chart",
		"chart_name": self.building_name + " Chart",
		"chart_type": "Report",
		"report_name": "Property Wise Unit Status",
		"use_report_chart": 0,
		"x_field": "property",
		"group_by_type": "Count",
		"number_of_groups": 0,
		"is_public": 1,
		"timespan": "Last Year",
		"time_interval": "Yearly",
		"timeseries": 0,
		"type": "Bar",
		"filters_json": json.dumps({"property": self.name}),
		"dynamic_filters_json": "{}",
		"custom_options": "",
		"roles": [],
		"y_axis": [
			{
				"y_field": "available",
				"color": "#29CD42"
			},
			{
				"y_field": "booked",
				"color": "#4463F0"
			},
			{
				"y_field": "leased",
				"color": "#EC864B"
			},
			{
				"y_field": "sold",
				"color": "#f70f0f"
			},
			{
				"y_field": "not_hand_over",
				"color": "#ED6396"
			}
		]
	})
	new_chart.insert()
	new_dashboard = frappe.get_doc({
		"doctype": "Dashboard",
		"dashboard_name": self.building_name + " Dashboard",
		"is_default": 0,
		"is_standard": 0,
		"cards": [
			{
				"card": self.building_name + " Total Units",  #1
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Booked Units", #11
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Leased Units", #16
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Sold Units", #21
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Available Units", #6
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Rented Total Units",  #2
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Rented Available Units", #7
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Rented Booked Units", #12
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Rented Leased Units", #17
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential - Rented Sold Units", #22
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Rented Not Handed Over Units", #27
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Sale Available Units", #8
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Sale Total Units",  #3
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Sale Not Hand Over Units", #28
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Sale Booked Units", #13
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Residential-Sale Leased Units", #18
				"doctype": "Number Card Link"
			},
				{
				"card": self.building_name + " Residential-Sale Sold Units", #23
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Total Units", #4
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Available Units", #9
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Booked Units", #14
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Leased Units", #19
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Sold Units", #24
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Commercial Not Hand Over Units", #29
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Total Units", #5
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Available Units", #10
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Booked Units", #15
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Leased Units", #20
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Sold Units", #25
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Parking Not Hand Over Units", #30
				"doctype": "Number Card Link"
			},
			{
				"card": self.building_name + " Not Hand Over Units", #26
				"doctype": "Number Card Link"
			},
		],
		"charts": [
			{
				"chart": self.building_name + " Chart",
				"doctype": "Dashboard Chart Link"
			}
		]
	})
	new_dashboard.insert()
	frappe.msgprint("Dashboard also created")