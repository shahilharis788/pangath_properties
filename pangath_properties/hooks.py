app_name = "pangath_properties"
app_title = "Pangath Properties"
app_publisher = "iterative"
app_description = "Real Estate App"
app_email = "iterative@example.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "pangath_properties",
# 		"logo": "/assets/pangath_properties/logo.png",
# 		"title": "Pangath Properties",
# 		"route": "/pangath_properties",
# 		"has_permission": "pangath_properties.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pangath_properties/css/pangath_properties.css"
# app_include_js = "/assets/pangath_properties/js/pangath_properties.js"

# include js, css files in header of web template
# web_include_css = "/assets/pangath_properties/css/pangath_properties.css"
# web_include_js = "/assets/pangath_properties/js/pangath_properties.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pangath_properties/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
fixtures = [
		{
			"dt": "Custom Field",
			"filters": [
				[
					"name",
					"in",
					(
						"Issue-unit",
						"Issue-property",
						"Maintenance Schedule-issue",
						"Maintenance Schedule Item-email",
						"Maintenance Schedule-custom_contact_number",
                        "Maintenance Schedule-custom_unit_no",
                        "Maintenance Schedule-custom_property",
                        "Maintenance Schedule-custom_tenancy_contract",
						"Sales Person-email",
						"Customer-property_name",
						"Customer-unit_name",
						"Payment Entry-tenant_onboarding",
						"Payment Entry-tenant_onboarding_termination",
						"Payment Entry-status_je",
						"Payment Entry-journal_entry",
						"Journal Entry-tenant_onboarding",
						"Journal Entry-tenant_onboarding_termination",
						"Journal Entry-pe_created",
						"Journal Entry-status",
						"Company-default_rental_income",
						"Journal Entry-payment_entry",
						"Customer-custom_emirate_id",
                        "Issue-custom_tenancy_contract",
                        "Issue-property",
                        "Issue-unit",
                        "Maintenance Visit-custom_tenancy_contract",
                        "Maintenance Visit-custom_property",
                        "Maintenance Visit-custom_issue",
                        "Maintenance Visit-custom_unit_no",
                        "Maintenance Visit-custom_tenant_signature",
                        "Maintenance Visit-custom_section_break_mnnxp",
                        "Material Request-custom_maintenance_visit",
                        "Sales Invoice-custom_maintenance_visit",
						"Opportunity-custom_property_and_units",
						"Opportunity-custom_property",
						"Opportunity-custom_property_and_unit",
						"Opportunity-custom_lead_type",
						"Lead-custom_for_rental",
						"Lead-custom_for_sale",
						"Opportunity-custom_for_rental",
						"Opportunity-custom_for_sale",
						"Lead-custom_parking_required",
						"Opportunity-custom_parking_required",
						"Payment Entry-custom_tenancy_contract",
						"Sales Invoice-custom_tenancy_contract",
						"Journal Entry-custom_tenancy_contract",
						"Payment Entry-custom_tenancy_application",
						"Quotation Item-custom_current_rate",
						"Quotation-custom_payment_frequency",
                        "Customer-custom_nationality",
                        "Customer-custom_contact_no",
                        "Customer-custom_passport_no",
                        "Stock Entry-custom_maintenance_visit",
                        "Material Request-custom_maintenance_schedule",
                        # TC
                        "Tenancy Contract-cusPayment Entry-custom_cheque_issue_datetom_opportunity",
                        #mode of payment
                        "Mode of Payment-custom_is_pdc",
                        # payment entry
                        "Payment Entry-custom_cheque_issue_date",
                        "Payment Entry-custom_is_pdc",
                        # sales invoice
                        'Sales Invoice-custom_bank_details',
                        'Sales Invoice-custom_bank_account',
                        "Sales Invoice-custom_inter_company_purchase_invoice_reference",
                        "Sales Invoice Item-custom_proforma_invoice",
                        'Sales Invoice-custom_naming_prefix'
                        # payemnt entry
                        'Payment Entry-custom_clearing_bank_account',
                        'Lead-custom_unit_status',
                        'Lead-custom_unit',
                        #customer
                        'Customer-custom_trade_licence',
                        #company
                        'Company-custom_naming_prefix',
                        #purchase invoice
                        'Purchase Invoice-custom_naming_prefix',
                        # journal entry
                        'Journal Entry-custom_naming_perfix',
                        # sales invoice
                        'Sales Invoice-custom_naming_prefix',
						'Lead-custom_property',
						'Type Of Charges-custom_is_scheduled_payment',
						'Mode of Payment Account-custom_bank_clearance_account',
						'Lead-custom_property',
						'Company-custom_naming_prefix',
						'Sales Invoice-custom_naming_prefix',
						'Purchase Invoice-custom_naming_prefix',
						'Journal Entry-custom_naming_perfix',
						'Customer-custom_emirate_id',
						'Company-custom_signatory_details',
						'Company-custom_name_of_authorised_signatory',
						'Company-custom_email_address',
						'Company-custom_column_break_dihvo',
						'Company-custom_position',
						'Company-custom_contact_number',
						'Company-custom_emirate_id'
					),
				]
			],
		},
		{
			"dt": "Property Setter",
			"filters": [
					[
						"doc_type",
						"in",
						(
							"Maintenance Schedule Detail",
							"Issue",
							"Maintenance Schedule Item",
							"Purchase Order",
							"Purchase Invoice",
							"Sales Order",
							"Sales Invoice",
							"Payment Entry",
                            "Maintenance Visit",
                            "Maintenance Visit Purpose",
							"Lead",
							"Maintenance Schedule",
							"Customer",
                            "Opportunity",
                            "Sales Invoice Item"
						),
					]
			],
		},
		{
            "dt": "Workflow State",
            "filters": [
                ["name", "in", ["Draft"]]
            ]
        },
		{
            "dt": "Workflow",
            "filters": [
                ["name", "in", ["Tenancy Application"]]
            ]
        },
        {
			"dt": "Print Format",
			"filters": [
					[
						"name",
						"in",
						(
							"Tenancy Contract sample",
							"Payment Plan - New Tenancy & Renewal sample",
							"Payment voucher sample",
							"Tenancy Cancellation sample",
							"Clearance for Tenant sample",
							"Move Out Checklist sample",
							"Receipt Voucher sample",
							"Internal Contract sample",
                            "Utility Summary sample",
                            "Tenant Information Form sample",
                            "Local Purchase Order sample",
                            "Tenancy Cancellation NOC sample",
                            "Quotation sample"
						),
					]
			],
		},
		{
            "dt": "Translation",
            "filters": [
                ["name", "in", ["44rq0frbjk", "59plq27d2l", "gaddrqhdbb"]]
            ]
        },
]

doctype_js = {
		"Opportunity": "public/js/opportunity.js",
		"Issue": "public/js/issue.js",
		"Payment Entry": "public/js/payment_entry.js",
		"Purchase Invoice": "public/js/purchase_invoice.js",
		"Purchase Order": "public/js/purchase_order.js",
		"Sales Order": "public/js/sales_order.js",
		"Sales Invoice": "public/js/sales_invoice.js",
		"Journal Entry": "public/js/journal_entry.js",
        	"Maintenance Visit":"public/js/maintenance_visit.js",
		"Maintenance Schedule":"public/js/maintenance_schedule.js",
        	"Quotation":"public/js/quotation.js",
        	"Company":"public/js/company.js",
		"Lead":"public/js/lead.js"
        
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "pangath_properties/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "pangath_properties.utils.jinja_methods",
# 	"filters": "pangath_properties.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pangath_properties.install.before_install"
after_install = "pangath_properties.setup.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pangath_properties.uninstall.before_uninstall"
# after_uninstall = "pangath_properties.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "pangath_properties.utils.before_app_install"
# after_app_install = "pangath_properties.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "pangath_properties.utils.before_app_uninstall"
# after_app_uninstall = "pangath_properties.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pangath_properties.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payment Entry": "pangath_properties.events.payment_entry.CustomPaymentEntry",
	"Maintenance Schedule": "pangath_properties.events.maintenance_schedule.CustomMaintenanceSchedule",
	"Maintenance Visit": "pangath_properties.events.maintenance_visit.CustomMaintenanceVisit"


}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
		"Payment Entry": {
				"on_submit": "pangath_properties.events.payment_entry.on_submit",
				"on_cancel": "pangath_properties.events.payment_entry.on_cancel",
				"before_submit":"pangath_properties.events.payment_entry.before_submit",
                # "after_insert": "pangath_properties.events.payment_entry.after_insert"
		},
		"Journal Entry": {
			"on_cancel": "pangath_properties.events.journal_entry.on_cancel",
			"validate": "pangath_properties.events.journal_entry.validate"
			},
		"Issue": {
			"before_validate": "pangath_properties.events.issue.validate"
			},
		"Maintenance Visit": {
            		"on_submit":"pangath_properties.events.maintenance_visit.change_status",
		},
        	"Purchase Invoice":{
            		"after_insert":"pangath_properties.events.purchase_invoice.after_insert_purchase_invoice"
		},
		"Maintenance Schedule":{
			"validate": "pangath_properties.events.maintenance_schedule.validate_tenancy_property"
		}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": "pangath_properties.pangath_properties.doctype.tenant_onboarding.tenant_onboarding.monthly_scheduler",
				
}

# Testing
# -------

# before_tests = "pangath_properties.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pangath_properties.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pangath_properties.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["pangath_properties.utils.before_request"]
# after_request = ["pangath_properties.utils.after_request"]

# Job Events
# ----------
# before_job = ["pangath_properties.utils.before_job"]
# after_job = ["pangath_properties.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pangath_properties.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

