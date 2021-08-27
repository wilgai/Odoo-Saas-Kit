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
    "name": "SaaS-Master:Base Module",
    "version": "1.0",
    "depends": ["base", "base_setup", 'purchase', "website_sale"],
    "author": "Pragmatic Techsoft Pvt. Ltd.",
    "category": "SaaS",
    "description": """
    Performs some basic functions to setup saas functionalities
""",
    'website': 'http://www.pragtech.co.in',
    'init_xml': [],
    'data': [
        'data/tenant_database_stage_data.xml',
        'security/saas_admin_security.xml',
        'security/ir.model.access.csv',
        'wizard/db_controll_view.xml',
        'views/base_admin_view.xml',
        'views/res_config_view.xml',
        'views/assets.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': True,
}
