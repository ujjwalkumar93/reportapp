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
			"fieldtype": "Link",
			"options": "Sales Invoice",
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
			"fieldname":"bal_qty",
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
def get_data(filters):
	data = []
	cond = "where docstatus = 1"
	# filter_data = {"docstatus":"1"}
	if filters:
		if filters.get("sales_order_no"):
			cond += " and name = '{0}'".format(filters.get("sales_order_no"))
			#filter_data['name'] = filters.get("sales_order_no")

		if filters.get("from_date") and filters.get("to_date"):
			cond += "and CAST(transaction_date as date) between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))
			

		if filters.get("status"):
			cond += " and status = '{0}'".format(filters.get("status"))
			#filter_data['name'] = filters.get("sales_order_no")
		if filters.get("customer"):
			cond += " and customer = '{0}'".format(filters.get("customer"))
			#filter_data['name'] = filters.get("sales_order_no")
		

	# all_so = frappe.db.get_all("Sales Order", filter_data,["name","transaction_date","status","customer"])
	query = """select name,transaction_date,status,customer from `tabSales Order` {0};""".format(cond)
	
	all_so = frappe.db.sql(query, as_dict = True)
	for so in all_so:
		item_bal_qty = []
		sec_item_bal = []

		item_bal_amt = []
		sec_bal_amt = []

		soi_wise_data = {}
		soi_wise_data['so_no'] = so.get("name")
		soi_wise_data['date'] = so.get("transaction_date")
		soi_wise_data['status'] = so.get("status")
		soi_wise_data['customer'] = so.get("customer")


		first_item = {}
		#data.append(soi_wise_data)
		so_items = frappe.db.get_all('Sales Order Item', {"parent": so.get('name')},['idx', 'item_code','qty','rate','amount'], order_by="item_code")
		
		for soi_pos, item in enumerate(so_items):
			si_item = fetch_si(so.get('name'),item.get('item_code'))
			if si_item:
				# on si
				if soi_pos == 0:
					for p,i in enumerate(si_item):
						si_date = str(frappe.db.get_value("Sales Invoice",{"name":i.get('parent')},['posting_date']))
						bal_qty = item.get('qty') - i.get('qty')
						transport = frappe.db.get_value("Sales Invoice", {"name": i.get("parent")}, ['transporter', 'lr_no'], as_dict= True)
						if p == 0:
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
							d['transporter_name'] = transport.get("transporter")
							d['transporter_lr_no'] = transport.get("lr_no")
							data.append(d)
						if p > 0:
							d = {}
							d['idx'] = si_item[0].get("idx")
							d['item_code'] = si_item[0].get("item_code")
							d['order_item_qty'] = item.get("qty")
							d['order_item_rate'] = item.get('rate')
							d['net_amount'] = item.get('amount')
							d['si_no'] = i.get('parent')
							d['si_date'] = si_date
							d['si_qty'] = i.get('qty')
							d['bal_qty'] = bal_qty
							d['transporter_name'] = transport.get("transporter")
							d['transporter_lr_no'] = transport.get("lr_no")
							data.append(d)
				#si_item = fetch_si(so.get('name'),item.get('item_code'))[1:]
				#for i in si_item:
				if soi_pos > 0:
					for i in si_item:
						d = {}
						d['idx'] = i.get("idx")
						d['item_code'] = i.get("item_code")
						d['order_item_qty'] = item.get("qty")
						d['order_item_rate'] = item.get('rate')
						d['net_amount'] = item.get('amount')
						d['si_no'] = i.get('parent')
						d['si_date'] = si_date
						d['si_qty'] = i.get('qty')
						d['bal_qty'] = bal_qty
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
	#print(sales_invoice_item)


			
			
			
			
			
			# if i == 0:
			# 	for pos,si_item in enumerate(sales_invoice_item):
			# 		if pos == 0:
			# 			soi_wise_data['idx'] = si_item.get('idx')
			# 			soi_wise_data['item_code'] = si_item.get('item_code')
			# 			soi_wise_data['order_item_qty'] = si_item.get('qty')
			# 			data.append(soi_wise_data)
			# 		else:
			# 			si_i_data = {}
			# 			si_i_data['idx'] = si_item.get('idx')
			# 			si_i_data['item_code'] = si_item.get('item_code')
			# 			si_i_data['order_item_qty'] = si_item.get('qty')
			# 			data.append(si_i_data)
			# else:
			# 	for pos,si_item in enumerate(sales_invoice_item):
			# 		pass
					# if item.get('idx') == si_item.get('idx') and item.get('item_code') == si_item.get('item_code'):
					# 	soi_wise_data['idx'] = si_item.get('idx')
					# 	soi_wise_data['item_code'] = si_item.get('item_code')
					# 	soi_wise_data['order_item_qty'] = si_item.get('qty')
						# data.append(soi_wise_data)
			# soi_without_inv['so_no'] = so.get("name")
			# soi_without_inv['date'] = so.get("transaction_date")
			# soi_without_inv['status'] = so.get("status")
			# soi_without_inv['customer'] = so.get("customer")
			# data.append(soi_without_inv)

		#data.append(soi_wise_data)

			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			# if(i == 0):
			# 	#item_dict = {}
			# 	soi_wise_data['idx'] = item.get("idx")
			# 	soi_wise_data['item_code'] = item.get("item_code")
			# 	soi_wise_data['order_item_qty'] = item.get('qty')
			# 	soi_wise_data['order_item_rate'] = item.get('rate')
			# 	soi_wise_data['net_amount'] = item.get('amount')
		
			# 	for pos,inv in enumerate(sales_invoice_item):
			# 		si_date = str(frappe.db.get_value("Sales Invoice",{"name":inv.get('parent')},['posting_date']))
			# 		bal_qty = item.get('qty') - inv.get('qty')
			# 		transport = frappe.db.get_value("Sales Invoice", {"name": inv.get("parent")}, ['transporter', 'lr_no'], as_dict= True)
			# 		if(pos==0):
			# 			item_bal_qty.clear()
			# 			item_bal_qty.append(bal_qty)
			# 			soi_wise_data['transporter_name'] = transport.get("transporter")
			# 			soi_wise_data['transporter_lr_no'] = transport.get("lr_no")
			# 			soi_wise_data['si_no'] = inv.get('parent')
			# 			soi_wise_data['si_qty'] = inv.get('qty')
			# 			soi_wise_data['si_date'] = si_date
			# 			soi_wise_data['bal_qty'] = bal_qty

			# 			paid_amt = item.get('rate') * inv.get('qty')
			# 			bal_amt = item.get('amount') - paid_amt

			# 			item_bal_amt.clear()
			# 			item_bal_amt.append(bal_amt)

			# 			soi_wise_data['balance_net_amt'] = bal_amt
			# 			# print('1', soi_wise_data)
			# 			# data.append(soi_wise_data)
			# 			# soi_wise_data.clear()
			# 		else:
			# 			b = 0
			# 			if item_bal_qty:
			# 				b = item_bal_qty[0] - inv.get('qty')
			# 				item_bal_qty.clear()
			# 				item_bal_qty.append(b)

			# 			amt = 0
			# 			if item_bal_amt:
			# 				amt = item_bal_amt[0] * item.get('rate') - b  * item.get('rate')
			# 				item_bal_amt.clear()
			# 				item_bal_amt.append(amt)

			# 			inv_dict = {}
			# 			inv_dict['transporter_name'] = transport.get("transporter")
			# 			inv_dict['transporter_lr_no'] = transport.get("lr_no")

			# 			inv_dict['idx'] = item.get('idx')
			# 			inv_dict['item_code'] = item.get('item_code')
			# 			inv_dict['si_no'] = inv.get('parent')
			# 			inv_dict['si_qty'] = inv.get('qty')
			# 			inv_dict['si_date'] = si_date
			# 			inv_dict['bal_qty'] = b

			# 			paid_amt = item.get('rate') * inv.get('qty')
			# 			bal_amt = item.get('amount') - paid_amt

			# 			inv_dict['balance_net_amt'] = amt
			# 			#print('2', inv_dict)
			# 			data.append(inv_dict)
			# 	#print('3',soi_wise_data)
			# 	if soi_wise_data:
			# 		# print("*"*100)
			# 		# print(soi_wise_data)
			# 		data.append(soi_wise_data)
			# else:
			# 	item_dict = {}
			# 	item_dict['idx'] = item.get("idx")
			# 	item_dict['item_code'] = item.get("item_code")
			# 	item_dict['order_item_qty'] = item.get('qty')
			# 	item_dict['order_item_rate'] = item.get('rate')
			# 	item_dict['net_amount'] = item.get('amount')
				
			# 	for pos,inv in enumerate(sales_invoice_item):
			# 		si_date = str(frappe.db.get_value("Sales Invoice",{"name":inv.get('parent')},['posting_date']))
			# 		bal_qty = item.get('qty') - inv.get('qty')
			# 		transport = frappe.db.get_value("Sales Invoice", {"name": inv.get("parent")}, ['transporter', 'lr_no'], as_dict= True)
			# 		if(pos==0):
			# 			sec_item_bal.clear()
			# 			sec_item_bal.append(bal_qty)
			# 			item_dict['si_no'] = inv.get('parent')
			# 			item_dict['si_qty'] = inv.get('qty')
			# 			item_dict['si_date'] = si_date
			# 			item_dict['bal_qty'] = bal_qty
			# 			item_dict['transporter_name'] = transport.get("transporter")
			# 			item_dict['transporter_lr_no'] = transport.get("lr_no")
			# 			#print('4', item_dict)
			# 			data.append(item_dict)
			# 		else:
			# 			mb = 0
			# 			if sec_item_bal:
			# 				#print('sec_item_bal[0]:',sec_item_bal[0])
			# 				mb = sec_item_bal[0] - inv.get('qty')
			# 				sec_item_bal.clear()
			# 				sec_item_bal.append(mb)
			# 			inv_data = {}
			# 			inv_data['idx'] = item.get("idx")
			# 			inv_data['item_code'] = item.get("item_code")
			# 			inv_data['si_no'] = inv.get('parent')
			# 			inv_data['si_qty'] = inv.get('qty')
			# 			inv_data['si_date'] = si_date
			# 			inv_data['bal_qty'] = mb
			# 			inv_data['transporter_name'] = transport.get("transporter")
			# 			inv_data['transporter_lr_no'] = transport.get("lr_no")
			# 			#print('5', inv_data)
			# 			data.append(inv_data)
			# 	#print('6', item_dict)
			# 	data.append(item_dict)
	
	#return data