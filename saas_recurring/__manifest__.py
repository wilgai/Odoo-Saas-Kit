# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name": "SaaS-Master:Recurring Invoices",
    "version": "1.0",
    "depends": ["base", 'payment', "base_setup", "payment_transfer", "website", 'purchase', "website_sale", "saas_sale"],

    "author": "Pragmatic Techsoft Pvt. Ltd.",
    "category": "SaaS",
    "description": """
    Generates the Recurring Invoices
""",
    'website': 'http://www.pragtech.co.in',
    'init_xml': [],
    'data': [
        'data/recurring_orders_data.xml',
        'data/schedule.xml',
        'views/recurring_orders_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
}
