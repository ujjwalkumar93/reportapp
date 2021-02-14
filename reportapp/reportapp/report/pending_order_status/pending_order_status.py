# Copyright (c) 2013, ujjwal and contributors
# For license information, please see license.txt

# from _future_ import unicode_literals
# import frappe
# from frappe import _
from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data
def get_columns():
	columns = [
       {
			"fieldname":"so_no",
			"label": _("Sales Order No"),
			"fieldtype": "Data",
			# "options": "Sales Order",
			"width": "100px"
		},
		{
			"fieldname":"date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": "100px"
		},
		{
			"fieldname":"status",
			"label": _("Status"),
			"fieldtype": "Select",
			"options": "To Deliver and Bill\nTo Bill\nTo Deliver\nCompleted",
			"width": "100px"
		},
		{
			"fieldname":"customer",
			"label": _("Customer"),
			"fieldtype": "Data",
			# "options": "Customer",
			"width": "100px"
		},

		{
			"fieldname":"idx",
			"label": _("Line Item No"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"item_code",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": "100px"
		},
		# {
		# 	"fieldname":"to_",
		# 	"label": ("To Date"),
		# 	"fieldtype": "Date",
		# 	"width": "100px"
		# },

		{
			"fieldname":"order_item_qty",
			"label": _("Order Item Qty"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"order_item_rate",
			"label": _("Order Item Rate"),
			"fieldtype": "Data",
			"width": "100px"
		},

		{
			"fieldname":"net_amount",
			"label": _("Net Amount"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"si_no",
			"label": _("Invoice Number"),
			"fieldtype": "Data",
			# "option": "Sales Invoice",
			"width": "100px"
		},

		{
			"fieldname":"si_date",
			"label": _("Invoice Date"),
			"fieldtype": "Date",
			"width": "100px"
		},

		{
			"fieldname":"si_qty",
			"label": _("Invoice Qty"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"balance_qty",
			"label": _("Balance Qty"),
			"fieldtype": "Data",
			"width": "100px"
		},

		{
			"fieldname":"balance_net_amt",
			"label": _("Balance Net Amt"),
			"fieldtype": "Data",
			"width": "100px"
		},

		{
			"fieldname":"transporter_name",
			"label": _("Trasporter Name"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"transporter_lr_no",
			"label": _("Transporter LR No"),
			"fieldtype": "Data",
			"width": "100px"
		},

    ]

	return columns
def get_data():
	data = []
	all_so = frappe.db.get_all("Sales Order", {"docstatus":"1"},["name","transaction_date","status","customer"])
	for so in all_so:
		so_wise_data = {}
		so_wise_data['so_no'] = so.get("name")
		so_wise_data['date'] = so.get("transaction_date")
		so_wise_data['status'] = so.get("status")
		so_wise_data['customer'] = so.get("customer")
		#data.append(so_wise_data)
		so_items = frappe.db.get_all('Sales Order Item', {"parent": so.get('name')},['idx', 'item_code','qty','rate','amount'], order_by="idx")
		for i, item in enumerate(so_items):
			sales_invoice = frappe.db.get_all("Sales Invoice Item", {'sales_order':so.get("name"), "item_code":item.get("item_code"),'docstatus':'1'},['parent','qty'])
			if(i == 0):
				item_dict = {}
				so_wise_data['idx'] = item.get("idx")
				so_wise_data['item_code'] = item.get("item_code")
				so_wise_data['order_item_qty'] = item.get('qty')
				so_wise_data['order_item_rate'] = item.get('rate')
				so_wise_data['net_amount'] = item.get('amount')
				#data.append(so_wise_data)	
				for pos,inv in enumerate(sales_invoice):
					if(pos==0):
						so_wise_data['si_no'] = inv.get('parent')
						so_wise_data['qty'] = inv.get('qty')
						data.append(so_wise_data)
					else:
						inv_dict = {}
						inv_dict['si_no'] = inv.get('parent')
						inv_dict['qty'] = inv.get('qty')
						data.append(inv_dict)
			else:
				item_dict = {}
				item_dict['idx'] = item.get("idx")
				item_dict['item_code'] = item.get("item_code")
				item_dict['order_item_qty'] = item.get('qty')
				item_dict['order_item_rate'] = item.get('rate')
				item_dict['net_amount'] = item.get('amount')
				#data.append(item_dict)
				# if sales_invoice:
				# if sales_invoice:
				for pos,inv in enumerate(sales_invoice):
					if(pos==0):
						item_dict['si_no'] = inv.get('parent')
						item_dict['si_qty'] = inv.get('qty')
						data.append(item_dict)
					else:
						inv_data = {}
						inv_data['si_no'] = inv.get('parent')
						inv_data['si_qty'] = inv.get('qty')
						data.append(inv_data)
				# else:
				# 	data.append(item_dict)
	return data