# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import itertools
from lxml import etree
import odoo
# from mx.DateTime import RelativeDateTime
# import mx.DateTime
import datetime
from odoo import models, fields, api, _

from odoo.exceptions import UserError, RedirectWarning, ValidationError
from dateutil.relativedelta import relativedelta
ADMINUSER_ID = 2
import xmlrpc.client



class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):

        values = super(AccountPayment, self).post()
        print("self._context:::::::::::::", self._context, self)

        if 'active_id' in self._context:
            move = self.env['account.move'].browse(self._context['active_id'])

            so_obj = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)

            if so_obj.saas_order:
                db_name = so_obj.instance_name
                tenant_db = self.env['tenant.database.list'].search([('name', '=', db_name)])

                ## XMLRPC CONNECTION
                ICPSudo = self.env['ir.config_parameter'].sudo()
                brand_website = ICPSudo.search([('key', '=', 'brand_website')]).value
                brand_admin = ICPSudo.search([('key', '=', 'admin_login')]).value
                brand_pwd = ICPSudo.search([('key', '=', 'admin_pwd')]).value
                dest_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(brand_website))
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(brand_website))
                uid_dst = common.authenticate(db_name, brand_admin, brand_pwd, {})

                config = odoo.tools.config
                agreement = self.env['sale.recurring.orders.agreement'].sudo().search([('instance_name', '=', db_name)])
                if not agreement:
                    print("\n\n\n inside not aggreement condition \n\n")

                ## FOR DIFFERENT SUBSCRIPTION TERMS TAKE RESPECTIVE NO .OF MONTHS
                months_to_add = 0
                term_type = tenant_db.sale_order_ref.invoice_term_id.type
                if term_type == 'from_first_date': months_to_add = 1
                if term_type == 'quarter': months_to_add = 3
                if term_type == 'half_year': months_to_add = 6
                if term_type == 'year': months_to_add = 12

                ## IF ALL PENDING INVOICES PAID, ALLOW TO ACTIVE DB
                allow_to_active_db = True

                if so_obj:
                    # parent_inv = self.env['account.move'].search([('name', '=', self.ref)]).ids
                    draft_invoices_ids_so = self.env['account.move'].search([('id', 'not in', [move.id]),
                                                                             ('invoice_origin', '=', so_obj.name),
                                                                             ('invoice_payment_state', 'not in',
                                                                              ['paid']),
                                                                             ('state', 'not in', ['cancel'])])
                    if draft_invoices_ids_so:
                        allow_to_active_db = False

                if allow_to_active_db:
                    new_exp_date = False

                    ## CALCULATE TENANT'S 'NEW_EXP_DATE' FROM IT'S SUBSCRIPTION TERM.
                    if not new_exp_date:
                        ## IF SUBSCRIPTION PERIOD IS MONTHLY AND 3 INVOICES ARE MISSED.
                        ## IN THIS CASE WE ADDED 3 MONTHS TO GET 'NEW_EXP_DATE', I.E. 'NEW_EXP_DATE' SHOULD BE GREATER THAN TODAY'S DATE
                        new_exp_date = tenant_db.exp_date

                        expiry_date_changed = False
                        current_exp_date = tenant_db.exp_date
                        current_exp_date = str(tenant_db.exp_date).split('-')
                        y = current_exp_date[0]
                        m = current_exp_date[1]
                        d = current_exp_date[2]
                        current_exp_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()

                        if current_exp_date > datetime.datetime.now().date():
                            new_exp_date = current_exp_date
                            expiry_date_changed = True

                        if not expiry_date_changed:
                            while True:
                                new_exp_date = str(
                                    datetime.datetime.strptime(str(new_exp_date), '%Y-%m-%d') + relativedelta(
                                        months=+months_to_add))[:10]

                                new_exp_date = new_exp_date.split('-')
                                y = new_exp_date[0]
                                m = new_exp_date[1]
                                d = new_exp_date[2]
                                new_exp_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()
                                today = datetime.datetime.now().date()
                                if new_exp_date > today:
                                    break

                    print("new expire date:", new_exp_date)

                    if config['db_user']:
                        self._cr.execute(
                            "ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': db_name, 'role': config['db_user']})

                    active_stage_id = self.env['tenant.database.stage'].search([('is_active', '=', True)], limit=1)

                    db_expire = dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'db.expire', 'search',
                                                      [[]])
                    for msg in db_expire:
                        print("innnnnnnnnnnnnnnnn", msg)
                        dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'db.expire', 'write',
                                              [msg,
                                               {
                                                   'db_expire': False,
                                               }]
                                              )

                    tenant_db.write({'free_trial': False,
                                     'expired': False,
                                     'exp_date': new_exp_date,
                                     'stage_id': active_stage_id.id or False
                                     })

                    service_ids = dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'saas.service', 'search', [[]])
                    for service_id in service_ids:
                        dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'saas.service', 'write',
                                              [service_id,
                                               {
                                                   'expiry_date': new_exp_date
                                               }]
                                              )

                mail_template_id = self.env['ir.model.data'].get_object_reference(
                    'saas_sale', 'email_template_renew_subscription')

                self.env['mail.template'].browse(mail_template_id[1]).send_mail(tenant_db.id, force_send=True)

                for item in move.invoice_line_ids:
                    if item.add_user_line:
                        print(move.user_count, tenant_db.no_of_users, type(datetime.datetime.today().date()),
                              'COUNTTTTTTTTTTTTTTTTT')

                        self.env['user.history'].sudo().create({
                            'tenant_id': tenant_db.id,
                            'pre_users': tenant_db.no_of_users,
                            'adding': move.user_count,
                            'total': tenant_db.no_of_users + move.user_count,
                            'rec_date': datetime.datetime.today().date(),
                        })
                        print("history created..........")

                        service_ids = dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'saas.service', 'search', [[]])
                        for service_id in service_ids:
                            dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'saas.service', 'write',
                                                  [service_id,
                                                   {
                                                       'user_count': move.user_count + tenant_db.no_of_users
                                                   }]
                                                  )
                        tenant_db.no_of_users = tenant_db.no_of_users + move.user_count

        return values


    
    

class account_invoice_line(models.Model):
    _inherit = "account.move.line"

    remove_user_line = fields.Boolean(string="User remove Invoice line")
    add_user_line = fields.Boolean(string="User add Invoice line")
    price_unit_show = fields.Float("Price")
    
    
    def write(self, vals):
        
        print (vals)
        
        return super(account_invoice_line, self).write(vals)

    










