import frappe
from real_estate.setup.install import after_install

def execute():
    after_install()
