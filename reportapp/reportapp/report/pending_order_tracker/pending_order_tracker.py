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
	data = get_data(filters)
	return columns, data
def get_columns():
	columns = [
       {
			"fieldname":"so_no",
			"label": _("Sales Order No"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "200px"
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
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": "100px"
		},
		{
			"fieldname":"order_item_rate",
			"label": _("Rate"),
			"fieldtype": "Currency",
			"width": "100px"
		},

		{
			"fieldname":"net_amount",
			"label": _("Net Amount"),
			"fieldtype": "Currency",
			"width": "100px"
		},
		{
			"fieldname":"si_no",
			"label": _("Invoice Number"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "150px"
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
			"fieldname":"bal_qty",
			"label": _("Balance Qty"),
			"fieldtype": "Data",
			"width": "100px"
		},

		{
			"fieldname":"bal_amt",
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
def get_data(filters):
	data = []
	cond = "where docstatus = 1"
	# filter_data = {"docstatus":"1"}
	if filters:
		if filters.get("sales_order_no"):
			cond += " and name = '{0}'".format(filters.get("sales_order_no"))
			#filter_data['name'] = filters.get("sales_order_no")

		if filters.get("from_date") and filters.get("to_date"):
			cond += " and CAST(transaction_date as date) between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))
			

		if filters.get("status"):
			cond += " and status = '{0}'".format(filters.get("status"))
			#filter_data['name'] = filters.get("sales_order_no")
		if filters.get("customer"):
			cond += " and customer = '{0}'".format(filters.get("customer"))
			#filter_data['name'] = filters.get("sales_order_no")
		

	# all_so = frappe.db.get_all("Sales Order", filter_data,["name","transaction_date","status","customer"])
	query = """select name,transaction_date,status,customer from `tabSales Order` {0} order by name desc;""".format(cond)
	
	all_so = frappe.db.sql(query, as_dict = True)
	for so in all_so:
		item_bal_qty = []
		

		item_bal_amt = []
		sec_bal_amt = []

		soi_wise_data = {}
		soi_wise_data['so_no'] = so.get("name")
		soi_wise_data['date'] = so.get("transaction_date")
		soi_wise_data['status'] = so.get("status")
		soi_wise_data['customer'] = so.get("customer")


		first_item = {}
		#data.append(soi_wise_data)
		so_items = frappe.db.get_all('Sales Order Item', {"parent": so.get('name')},['idx', 'item_code','qty','rate','amount'], order_by="idx")
		q = """select idx,item_code,qty,rate,amount from `tabSales Order Item` where parent = '{0}' order by idx asc""".format(so.get('name'))
		#so_items = frappe.db.sql(q, as_dict = True)
		for soi_pos, item in enumerate(so_items):
			print('---------')
			print(item)
			si_item = fetch_si(so.get('name'),item.get('item_code'))
			if si_item:
				# on si
				if soi_pos == 0:
					for p,i in enumerate(si_item):
						si_date = str(frappe.db.get_value("Sales Invoice",{"name":i.get('parent')},['posting_date']))
						bal_qty = item.get('qty') - i.get('qty')
						transport = frappe.db.get_value("Sales Invoice", {"name": i.get("parent")}, ['transporter', 'lr_no'], as_dict= True)
						bal_amt = item.get('amount') - (i.get('qty') * item.get('rate'))
						if p == 0:
							item_bal_qty.clear()
							item_bal_qty.append(bal_qty)

							item_bal_amt.clear()
							item_bal_amt.append(bal_amt)
							d = {}
							d['so_no'] = so.get("name")
							d['date'] = so.get("transaction_date")
							d['status'] = so.get("status")
							d['customer'] = so.get("customer")
							d['idx'] = si_item[0].get("idx")
							d['item_code'] = si_item[0].get("item_code")
							d['order_item_qty'] = item.get("qty")
							d['order_item_rate'] = item.get('rate')
							d['net_amount'] = item.get('amount')
							d['si_no'] = i.get('parent')
							d['si_date'] = si_date
							d['si_qty'] = i.get('qty')
							d['bal_qty'] = bal_qty
							d['bal_amt'] = bal_amt
							d['transporter_name'] = transport.get("transporter")
							d['transporter_lr_no'] = transport.get("lr_no")
							# if bal_qty > 0:
							data.append(d)
						if p > 0:
							b = 0
							if item_bal_qty:
								b = item_bal_qty[0] - i.get('qty')
								item_bal_qty.clear()
								item_bal_qty.append(b)
							a = 0
							if item_bal_amt:
								a = item_bal_amt[0] - (i.get('qty') * item.get('rate'))
								item_bal_amt.clear()
								item_bal_amt.append(a)
							d = {}
							d['so_no'] = so.get("name")
							d['date'] = so.get("transaction_date")
							d['status'] = so.get("status")
							d['customer'] = so.get("customer")
							d['idx'] = si_item[0].get("idx")
							d['item_code'] = si_item[0].get("item_code")
							# d['order_item_qty'] = item.get("qty")
							# d['order_item_rate'] = item.get('rate')
							# d['net_amount'] = item.get('amount')
							d['si_no'] = i.get('parent')
							d['si_date'] = si_date
							d['si_qty'] = i.get('qty')
							d['bal_qty'] = b
							d['bal_amt'] = a
							d['transporter_name'] = transport.get("transporter")
							d['transporter_lr_no'] = transport.get("lr_no")
							# if b > 0:
							print("#############")
							print(b)
							data.append(d)
				#si_item = fetch_si(so.get('name'),item.get('item_code'))[1:]
				#for i in si_item:
				if soi_pos > 0:
					for p,i in enumerate(si_item):
						bal_qty = item.get('qty') - i.get('qty')
						bal_amt = item.get('amount') - (i.get('qty') * item.get('rate'))
						if p == 0:
							item_bal_qty.clear()
							item_bal_qty.append(bal_qty)
							item_bal_amt.clear()
							item_bal_amt.append(bal_amt)
							d = {}
							d['so_no'] = so.get("name")
							d['date'] = so.get("transaction_date")
							d['status'] = so.get("status")
							d['customer'] = so.get("customer")
							d['idx'] = i.get("idx")
							d['item_code'] = i.get("item_code")
							d['order_item_qty'] = item.get("qty")
							d['order_item_rate'] = item.get('rate')
							d['net_amount'] = item.get('amount')
							d['si_no'] = i.get('parent')
							d['si_date'] = si_date
							d['si_qty'] = i.get('qty')
							d['bal_amt'] = bal_amt
							d['bal_qty'] = bal_qty
							if bal_qty > 0:
								data.append(d)
						if p > 0:
							b = 0
							if item_bal_qty:
								b = item_bal_qty[0] - i.get('qty')
								item_bal_qty.clear()
								item_bal_qty.append(b)
							if item_bal_amt:
								a = item_bal_amt[0] - (i.get('qty') * item.get('rate'))
								item_bal_amt.clear()
								item_bal_amt.append(a)
							d = {}
							
							d['so_no'] = so.get("name")
							d['date'] = so.get("transaction_date")
							d['status'] = so.get("status")
							d['customer'] = so.get("customer")
							d['idx'] = i.get("idx")
							d['item_code'] = i.get("item_code")
							# d['order_item_qty'] = item.get("qty")
							# d['order_item_rate'] = item.get('rate')
							# d['net_amount'] = item.get('amount')
							d['si_no'] = i.get('parent')
							d['si_date'] = si_date
							d['si_qty'] = i.get('qty')
							d['bal_qty'] = b
							d['bal_amt'] = a
							#if b > 0:
							data.append(d)
			else:
				# on so
				if soi_pos == 0:
					soi_wise_data['idx'] = item.get("idx")
					soi_wise_data['item_code'] = item.get("item_code")
					soi_wise_data['order_item_qty'] = item.get("qty")
					soi_wise_data['order_item_rate'] = item.get('rate')
					soi_wise_data['net_amount'] = item.get('amount')
					data.append(soi_wise_data)
				
				if soi_pos > 0:
					d = {}
					d['so_no'] = so.get("name")
					d['date'] = so.get("transaction_date")
					d['status'] = so.get("status")
					d['customer'] = so.get("customer")
					d['idx'] = item.get("idx")
					d['item_code'] = item.get("item_code")
					d['order_item_qty'] = item.get("qty")
					d['order_item_rate'] = item.get('rate')
					d['net_amount'] = item.get('amount')
					data.append(d)
	return data

def fetch_si(name,item_code):
	data = frappe.db.get_all("Sales Invoice Item", {'sales_order':name, "item_code":item_code,'docstatus':'1'},['parent','qty','item_code','idx'], order_by= "item_code")
	return data
	