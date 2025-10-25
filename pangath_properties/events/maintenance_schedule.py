import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.maintenance.doctype.maintenance_schedule.maintenance_schedule import MaintenanceSchedule
from frappe.utils import cstr, getdate, add_days
from frappe import _
@frappe.whitelist()
def create_material_request(source_name, target_doc=None):
    if source_name:
        def set_missing_value(source,target):
            for i in target.items:
                i.unit = source.custom_unit_no
                i.property = source.custom_property
        doclist = get_mapped_doc("Maintenance Schedule", source_name, {
            "Maintenance Schedule": {
                "doctype": "Material Request",
                "field_map":{
                    "name":"custom_maintenance_schedule"
                }
               
            },
            "Maintenance Schedule Item": {
            "doctype": "Material Request Item",
            "field_map": [
            ],
      },

        }, target_doc,set_missing_value)
        return doclist

def validate_tenancy_property(doc, method=None):
    if not doc.custom_tenancy_contract:
        return
    property_of_tenant = frappe.db.get_value("Tenancy Contract", doc.custom_tenancy_contract, "property_name", pluck=True)
    if doc.custom_property != property_of_tenant:
        frappe.throw(f'Property does not belong to the Tenancy Contract {doc.custom_tenancy_contract}')


class CustomMaintenanceSchedule(MaintenanceSchedule):
    @frappe.whitelist()
    def generate_schedule(self):
        if self.docstatus != 0:
            return

        # Clear previous schedule
        self.set("schedules", [])
        count = 1

        for d in self.get("items"):
            self.validate_maintenance_detail()

            # Generate list of scheduled dates
            s_list = self.create_schedule_list(
                d.start_date, d.end_date, d.no_of_visits, d.sales_person
            )

            # Ensure unique dates only
            unique_dates = sorted(set(s_list))

            # Append child records only once per schedule_date
            for scheduled_date in unique_dates:
                child = self.append("schedules")
                child.item_code = d.item_code
                child.item_name = d.item_name
                # scheduled_date may be a date or string
                try:
                    child.scheduled_date = scheduled_date.strftime("%Y-%m-%d")
                except Exception:
                    child.scheduled_date = cstr(scheduled_date)

                if getattr(d, "serial_no", None):
                    child.serial_no = d.serial_no

                child.idx = count
                count += 1
                child.sales_person = d.sales_person
                child.completion_status = "Pending"
                child.item_reference = d.name

    def create_schedule_list(self, start_date, end_date, no_of_visit, sales_person):
        """Generate list of scheduled dates, handling same-day start and end."""
        schedule_list = []

        start_date = getdate(start_date)
        end_date = getdate(end_date)

        if no_of_visit < 1:
            return schedule_list

        if start_date == end_date:
            # If same start and end date, repeat the same date
            schedule_list = [start_date] * no_of_visit
        else:
            # Spread visits evenly between start and end date
            total_days = (end_date - start_date).days
            interval = total_days / (no_of_visit - 1) if no_of_visit > 1 else 0

            for i in range(no_of_visit):
                scheduled_date = add_days(start_date, round(i * interval))
                scheduled_date = self.validate_schedule_date_for_holiday_list(
                    scheduled_date, sales_person
                )
                if scheduled_date > end_date:
                    scheduled_date = end_date
                schedule_list.append(scheduled_date)

        return schedule_list

    def validate_maintenance_detail(self):
        if not self.get("items"):
            frappe.throw(_("Please enter Maintenance Details first"))

        for idx, d in enumerate(self.get("items"), start=1):
            if not d.item_code:
                frappe.throw(_("Please select item code for row {0}").format(idx))

            if not d.start_date or not d.end_date:
                frappe.throw(
                    _(
                        "Please select Start Date and End Date for Item {0} (Row {1})"
                    ).format(d.item_code or "Unknown", idx)
                )

            if not d.no_of_visits:
                frappe.throw(
                    _(
                        "Please mention no of visits required for Item {0} (Row {1})"
                    ).format(d.item_code or "Unknown", idx)
                )

            # Allow same start and end date
            if getdate(d.start_date) > getdate(d.end_date):
                frappe.throw(
                    _(
                        "Start date should be less than or equal to end date for Item {0} (Row {1})"
                    ).format(d.item_code or "Unknown", idx)
                )

    def on_submit(self):
        self.check_serial_no_added()
        self.validate_schedule()

        email_map = {}
        for d in self.get("items"):
            if d.serial_and_batch_bundle:
                serial_nos = frappe.get_doc(
                    "Serial and Batch Bundle", d.serial_and_batch_bundle
                ).get_serial_nos()

                if serial_nos:
                    self.validate_serial_no(d.item_code, serial_nos, d.start_date)
                    self.update_amc_date(serial_nos, d.end_date)

            no_email_sp = []
            if d.sales_person and d.sales_person not in email_map:
                sp = frappe.get_doc("Sales Person", d.sales_person)
                try:
                    email_map[d.sales_person] = sp.get_email_id()
                except frappe.ValidationError:
                    no_email_sp.append(d.sales_person)

            if no_email_sp:
                frappe.msgprint(
                    _(
                        "Setting Events to {0}, since the Employee attached to the below Sales Persons does not have a User ID{1}"
                    ).format(self.owner, "<br>" + "<br>".join(no_email_sp))
                )

            scheduled_date = frappe.db.get_all(
                "Maintenance Schedule Detail",
                {"parent": self.name, "item_code": d.item_code},
                ["scheduled_date"],
                as_list=False,
            )

            for key in scheduled_date:
                description = frappe._(
                    "Reference: {0}, Item Code: {1} and Customer: {2}"
                ).format(self.name, d.item_code, self.customer)
                event = frappe.get_doc(
                    {
                        "doctype": "Event",
                        "owner": email_map.get(d.sales_person, self.owner),
                        "subject": description,
                        "description": description,
                        "starts_on": cstr(key["scheduled_date"]) + " 10:00:00",
                        "event_type": "Private",
                    }
                )
                event.add_participant(self.doctype, self.name)
                event.insert(ignore_permissions=1)

        self.db_set("status", "Submitted")