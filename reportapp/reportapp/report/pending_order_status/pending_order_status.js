// Copyright (c) 2016, ujjwal and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Order Status"] = {
	"filters": [
		{
			"fieldname":"sales_order_no",
			"label": __("Sales Order No"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "100px"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px"
		},

		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "To Deliver and Bill\nTo Bill\nTo Deliver\nCompleted",
			"width": "100px"
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100px"
		},

	]
};
