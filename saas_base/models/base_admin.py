import xmlrpc
from odoo import models, fields, api
import time
# from mx.DateTime import RelativeDateTime
# import mx.DateTime
from odoo.tools import config
import logging
from odoo.service import db
import odoo.addons.decimal_precision as dp
# from pragmatic_saas.saas_base.admin_user import ADMINUSER_ID
# from sass_base.admin_user import ADMINUSER_ID
from datetime import datetime as dt
import datetime
from odoo.exceptions import UserError, ValidationError

ADMINUSER_ID = 2
_logger = logging.getLogger(__name__)

from odoo.http import request


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    def _handle_website_page_visit(self, response, website_page, visitor_sudo):
        """ Called on dispatch. This will create a website.visitor if the http request object
        is a tracked website page or a tracked view. Only on tracked elements to avoid having
        too much operations done on every page or other http requests.
        Note: The side effect is that the last_connection_datetime is updated ONLY on tracked elements."""
        print("in patch...........")
        url = ""
        print(request.httprequest.__dict__, "\n AAAAAAABBBBBBBBCCCCCCCC")
        if 'environ' in request.httprequest.__dict__ and 'HTTP_REFERER' in request.httprequest.__dict__['environ']:
            url = request.httprequest.__dict__['environ']['HTTP_REFERER']
        else:
            url = request.httprequest.url

        website_track_values = {
            'url': url,
            'visit_datetime': dt.now(),
        }
        if website_page:
            website_track_values['page_id'] = website_page.id
            domain = [('page_id', '=', website_page.id)]
        else:
            domain = [('url', '=', url)]
        visitor_sudo._add_tracking(domain, website_track_values)
        if visitor_sudo.lang_id.id != request.lang.id:
            visitor_sudo.write({'lang_id': request.lang.id})


class tenant_database_stage(models.Model):
    _name = "tenant.database.stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence"

    def write(self, vals):
        if 'is_active' in vals:
            del vals['is_active']
        if 'is_grace' in vals:
            del vals['is_grace']
        if 'is_expired' in vals:
            del vals['is_expired']
        if 'is_purge' in vals:
            del vals['is_purge']
        if 'is_deactivated' in vals:
            del vals['is_deactivated']
        return super(tenant_database_stage, self).write(vals)

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.", default=1)
    fold = fields.Boolean('Folded in Kanban View',
                          help='This stage is folded in the kanban view when'
                               'there are no records in that stage to display.')
    is_active = fields.Boolean('Active', default=False)
    is_grace = fields.Boolean('Grace Period Over', default=False)
    is_expired = fields.Boolean('Expired', default=False)
    is_deactivated = fields.Boolean('Deactivated', default=False)
    is_purge = fields.Boolean('Purge', default=False)


tenant_database_stage()


class tenant_database_list(models.Model):
    _name = "tenant.database.list"
    _description = 'Tenant Database List'

    def _make_invoice(self):
        agreement_order_obj = self.env['sale.recurring.orders.agreement.order']
        invoice_line_obj = self.env['account.move.line']
        invoice_obj = self.env['account.move']
        journal_obj = self.env['account.journal']
        today = time.strftime('%Y-%m-%d')
        move_id = None



        ## check agreement is created for this tenant
        agreement_order_id = agreement_order_obj.sudo().search([('order_id', '=', self.sale_order_ref.id), ('agreement_id.active', '=', True)],
                                                               limit=1)
        if agreement_order_id:
            res = journal_obj.search([('type', '=', 'sale')], limit=1)
            journal_id = res and res[0] or False
            account_id = self.sale_order_ref.partner_id.property_account_receivable_id.id
            # invoice_vals = {
            #     'name': self.sale_order_ref.name,
            #     'invoice_origin': self.sale_order_ref.name,
            #     'comment': 'SaaS Recurring Invoice',
            #     'date_invoice': today,
            #     'address_invoice_id':self.sale_order_ref.partner_invoice_id.id,
            #     'user_id': self._uid,
            #     'partner_id':self.sale_order_ref.partner_id.id,
            #     'account_id':account_id,
            #     'journal_id':journal_id.id,
            #     'sale_order_ids': [(4,self.sale_order_ref.id)],
            #     'instance_name': str(self.name).encode('utf-8'),
            #     'agreement_id':agreement_order_id.agreement_id.id,
            #     'invoice_type': 'rent',
            # }
            # move_id = invoice_obj.create(invoice_vals)

            ## make invoice line from the agreement product line
            ICPSudo = self.env['ir.config_parameter'].sudo()
            user_product_id = int(ICPSudo.search([('key', '=', 'buy_product')]).value)


            invoice_vals = {
                'name':self.env['ir.sequence'].next_by_code('account.payment.customer.invoice'),
                'type': 'out_invoice',
                'invoice_origin': self.sale_order_ref.name,
                # 'comment': 'SaaS Recurring Invoice',
                'date': today,
                # 'address_invoice_id':self.sale_order_ref.partner_invoice_id.id,
                'user_id': self._uid,
                'partner_id': self.sale_order_ref.partner_id.id,
                # 'account_id':account_id,
                'journal_id': journal_id.id,
                # 'sale_order_ids': [(4,self.sale_order_ref.id)],
                'instance_name': str(self.name).encode('utf-8'),
                'agreement_id': agreement_order_id.agreement_id.id,
                'invoice_type': 'rent',
                'invoice_line_ids': [],
            }

            for line in agreement_order_id.agreement_id.agreement_line:
                qty = line.quantity
                months = 1
                if self.sale_order_ref.invoice_term_id.name == 'Yearly':
                    months=12
                else:
                    months = 1





                if user_product_id == line.product_id.id:
                    qty = self.sale_order_ref.no_of_users
                # invoice_line_vals = {
                #                     'name': line.product_id.name,
                #                     'origin': 'SaaS-Kit-'+line.agreement_id.number,
                #                     'move_id': move_id.id,
                #                     'uom_id': line.product_id.uom_id.id,
                #                     'product_id': line.product_id.id,
                #                     'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
                #                     'price_unit': line.product_id.lst_price,
                #                     'discount': line.discount,
                #                     'quantity': qty,
                #                     'account_analytic_id': False,
                #                     }
                invoice_line_vals = {
                    'name': line.product_id.name,
                    'price_unit': line.product_id.lst_price * months * self.no_of_users,
                    'price_unit_show': line.product_id.lst_price,
                    'quantity': 1,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_id.uom_id.id,
                    # 'price_subtotal': line.product_id.lst_price * months * self.sale_order_ref.no_of_users,
                    # 'tax_ids': [(6, 0, so_line.tax_id.ids)],
                    # 'sale_line_ids': [(6, 0, [so_line.id])],
                    # 'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                    'analytic_account_id': False,
                    # 'invoice_line_tax_ids':[[6, False, [line.product_id.taxes_id.id]]]
                }

                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

                # if line.product_id.taxes_id.id:
                #     invoice_line_vals['invoice_line_tax_ids'] = [[6, False, [line.product_id.taxes_id.id]]] #[(6, 0, [line.product_id.taxes_id.id])],

            inv = invoice_obj.create(invoice_vals)
            sequence = inv._get_sequence()
            name1 = sequence.next_by_id(sequence_date=inv.date)
            inv.name = name1

            # recompute taxes(Update taxes)
            # if move_id.invoice_line_ids: move_id.compute_taxes()
        #     return move_id
        #
        # #recompute taxes(Update taxes)
        # print (move_id,'====================================ss')
        # if move_id:
        #     if move_id.invoice_line_ids: move_id.compute_taxes()
        return move_id

    # added by krishna
    def send_saas_alert_email(self, alert_type):

        alert_no_of_days = 0
        result = False
        today = time.strftime('%Y-%m-%d')
        ICPSudo = self.env['ir.config_parameter'].sudo()

        if alert_type == 'free_trial':
            alert_no_of_days = int(ICPSudo.get_param('free_trail_no_of_days', default=7))
        elif alert_type == 'expire_db':
            alert_no_of_days = int(ICPSudo.get_param('db_expire_no_of_days', default=7))

        if str(self.exp_date) == str(datetime.datetime.now().date()):
            _logger.info('SaaS-Tenant %(db)s db expire today' % {'db': self.name})

            mail_template_id = self.env.ref('saas_base.email_template_renew_tenant_Expired_today', raise_if_not_found=False)
            result = mail_template_id.with_context(lang=self.sale_order_ref.partner_id.lang).send_mail(self.id,
                                                                                                       force_send=True,
                                                                                                       )

        if alert_no_of_days > 0:
            alertday = str(datetime.datetime.strptime(str(self.exp_date), '%Y-%m-%d') - datetime.timedelta(days=int(alert_no_of_days)))[:10]
            if (alertday == str(today)):
                _logger.info('SaaS-Invoice Generated for Tenant %(db)s' % {'db': self.name})

                mail_template_id = self.env.ref('saas_base.email_template_renew_tenant_subscription_alert', raise_if_not_found=False)
                result = mail_template_id.with_context(lang=self.sale_order_ref.partner_id.lang).send_mail(self.id, force_send=True,
                                                                                                           )

        if alert_type == 'grace_period_start':
            _logger.info('SaaS-Tenant %(db)s grace period started' % {'db': self.name})

            mail_template_id = self.env.ref('saas_base.email_template_tenant_db_grace_alert', raise_if_not_found=False)
            result = mail_template_id.with_context(lang=self.sale_order_ref.partner_id.lang).send_mail(self.id, force_send=True)

        ## if alert type is grace_period_start send email to tenant that database is ready to purge         
        if alert_type == 'ready_for_purge':
            _logger.info('SaaS-Tenant %(db)s ready to purge' % {'db': self.name})
            mail_template_id = self.env.ref('saas_base.email_template_tenant_db_purge_alert', raise_if_not_found=False)
            result = mail_template_id.with_context(lang=self.sale_order_ref.partner_id.lang).send_mail(self.id, force_send=True)

        return result

    def init(self):
        print("init called from tenant db list..........")
        cr = self._cr
        expired_db_role = 'expired_db_owner'
        bare_db = 'bare_tenant_13'
        db_name='saasmaster'
        cr.execute("SELECT 1 FROM pg_roles WHERE rolname='%(role)s'" % {'role': expired_db_role})
        role_exist = cr.fetchone()
        config['expired_db_owner'] = ""
        config['bare_db'] = ""
        config['db_name']= ""

        if not role_exist:
            cr.execute("create role %(role)s" % {'role': expired_db_role})
            config.__setitem__('expired_db_owner', expired_db_role)
            config.save()
            _logger.info('SaaS- Expired DB Role %(role)s created' % {'role': expired_db_role})
        else:
            config.__setitem__('expired_db_owner', expired_db_role)
            config.save()
        cr.execute("SELECT datname FROM pg_database WHERE datname='%(db)s'" % {'db': bare_db})
        db_exist = cr.fetchone()
        if not db_exist:
            db.exp_create_database(bare_db, False, 'en_US', 'admin')
            import odoo
            from odoo.api import Environment
            registry = odoo.registry(bare_db)
            bare_cr = registry.cursor()
            env = Environment(bare_cr, ADMINUSER_ID, {})
            module_obj = env['ir.module.module'].sudo()
            module_ids_to_install = module_obj.sudo().search([('name', 'in', ['base'])])
            try:
                for mod_install in module_ids_to_install:
                    mod_install.sudo().button_immediate_install()
            except:
                print('some issue raised')

            config.__setitem__('bare_db', bare_db)
            config.__setitem__('db_name', db_name)
            config.save()
            _logger.info('SaaS- Bare Database %(db)s created' % {'db': bare_db})
        else:
            config.__setitem__('bare_db', bare_db)
            config.__setitem__('db_name', db_name)
            config.save()

    def check_tenant_database_expire(self):
        """
        Overridden as it is 
        """
        _logger.info('SaaS-Db Expire db check start')

        # tenant_dbs = self.browse(self.search([]))
        cr = self._cr
        ## Find all databases list available
        server_db_list = []
        cr.execute("select datname from pg_database where datistemplate=false")
        cr_res = cr.fetchall()
        for item in cr_res:
            if item:
                server_db_list.append(item[0])

        import datetime
        today = datetime.datetime.now().date()
        print(today, '=================================today')
        for tenant_db in self.env['tenant.database.list'].search([]):

            ## Find configured grace and purging days
            ICPSudo = self.env['ir.config_parameter'].sudo()
            grace_days = int(ICPSudo.search([('key', '=', 'grace_period')]).value)
            purge_days = int(ICPSudo.search([('key', '=', 'data_purging_days')]).value)

            # if not tenant_db.expired:
            # Pulled outside of this if statement and if statement commented
            # ==========================Start=============================================
            ## check tenant database is in free trail or not
            if tenant_db.free_trial:

                tenant_db.send_saas_alert_email('free_trial')
            else:

                tenant_db.send_saas_alert_email('expire_db')

            ##check if db state in [active,grace,expired]
            in_allowed_stages = False
            print("tenant_db.stage_id.is_active", tenant_db.stage_id.is_active, tenant_db.stage_id.is_grace, tenant_db.stage_id.is_expired)
            if tenant_db.stage_id.is_active or tenant_db.stage_id.is_grace or tenant_db.stage_id.is_expired:
                in_allowed_stages = True

            if in_allowed_stages:
                ## if today is expire date then generate the invoice
                next_invoice_create_date = str(tenant_db.exp_date).split('-')
                y = next_invoice_create_date[0]
                m = next_invoice_create_date[1]
                d = next_invoice_create_date[2]
                next_invoice_create_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()

                ## if tenant database exp_date plus grace days is equal to today then deactivate database. Set stage to 'Expired'
                ##------------------------------Start--------------------------------------------
                graceperiod_date = str(datetime.datetime.strptime(str(tenant_db.exp_date), '%Y-%m-%d') + datetime.timedelta(days=int(grace_days)))[
                                   :10]
                ## graceperiod_date has format (y-m-d)
                graceperiod_date = graceperiod_date.split('-')
                y = graceperiod_date[0]
                m = graceperiod_date[1]
                d = graceperiod_date[2]
                graceperiod_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()

                print(graceperiod_date, tenant_db.name, 'SSSSSSSSSSSSSSSSSSr', today)

                if (graceperiod_date <= today and tenant_db.name in server_db_list):
                    # print("graceperiod_date:::::::::::::::::::::::::*************************************", graceperiod_date,tenant_db.name)

                    stage_ids = self.env['tenant.database.stage'].search([('is_grace', '=', True)], limit=1)
                    so_origin = tenant_db.sale_order_ref.name
                    ## Find related invoice ids which are in draft and open state
                    ## If found any, allow to expire DB, bcoz grace period is over and still invoices are not paid
                    related_invoice_ids = self.env['account.move'].search([('invoice_origin', '=', so_origin),
                                                                           ('state', 'in', ['draft', 'open'])])

                    ##Check if already state is set to expired.
                    current_stage_id = tenant_db.stage_id.id
                    print("current_stage_id:::::::::::", current_stage_id)

                    if current_stage_id not in stage_ids.ids and related_invoice_ids:
                        # print("IN EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",tenant_db.name)
                        tenant_db.write({'stage_id': stage_ids.id if stage_ids else False})
                        cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': tenant_db.name, 'role': 'expired_db_owner'})

                        brand_name = ICPSudo.search([('key', '=', 'brand_name')]).value
                        brand_website = ICPSudo.search([('key', '=', 'brand_website')]).value
                        brand_admin = ICPSudo.search([('key', '=', 'admin_login')]).value
                        brand_pwd = ICPSudo.search([('key', '=', 'admin_pwd')]).value

                        order = self
                        db_name = tenant_db.name
                        print("db_name:::::::;;", db_name)
                        dest_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(brand_website))
                        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(brand_website))
                        uid_dst = common.authenticate(db_name, brand_admin, brand_pwd, {})
                        db_expire = dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'db.expire', 'search',[[]])
                        for msg in db_expire:
                            print("innnnnnnnnnnnnnnnn", msg)
                            dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'db.expire', 'write',
                                                  [msg,
                                                   {
                                                       'db_expire': True,
                                                   }]
                                                  )

                        tenant_db.send_saas_alert_email('expired')

                ##-----------------------------End-------------------------------------------------

                ##grace period email
                tenant_exp_date = str(tenant_db.exp_date).split('-')
                y = tenant_exp_date[0]
                m = tenant_exp_date[1]
                d = tenant_exp_date[2]
                tenant_exp_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()
                days_calculate_missing_invoices = (today - tenant_exp_date).days
                months_to_add = 0

                if (tenant_exp_date <= today and tenant_db.name in server_db_list):
                    expire_stage_id = self.env['tenant.database.stage'].search([('is_expired', '=', True)], limit=1)
                    grace_stage_id = self.env['tenant.database.stage'].search([('is_grace', '=', True)], limit=1)

                    if tenant_db.stage_id.id != expire_stage_id.id and tenant_db.stage_id.id != grace_stage_id.id:
                        # if tenant_db.stage_id.id == expire_stage_id.id and tenant_db.stage_id.id != grace_stage_id.id:

                        ##Database should not in expire stage
                        ##And stage should not be equal to grace stage id. If it is same as grace stage id it means the invoice is already generated






                        tenant_db.write({'stage_id': expire_stage_id.id if grace_stage_id else False})
                        if tenant_exp_date > today:
                            tenant_db.write({'stage_id': grace_stage_id.id if grace_stage_id else False})

                        try:
                            tenant_db.send_saas_alert_email('grace_period_start')
                        except:
                            print("Issue in sending mail")

                        ## create invoice for the first time if moved to grace stage

                        # print("firstt invoice *******************************************************************************",tenant_db.name)
                        move_id = tenant_db._make_invoice()
                        if move_id:
                            print(333333333333333333333333333)
                            # move invoice in "Open" state
                            if move_id.invoice_line_ids: move_id.action_post()

                    ##create missed invoice if any
                    tenant_db.name
                    months_to_add = 0
                    term_type = tenant_db.sale_order_ref.invoice_term_id.type
                    if term_type == 'from_first_date': months_to_add = 1
                    if term_type == 'quarter': months_to_add = 3
                    if term_type == 'half_year': months_to_add = 6
                    if term_type == 'year': months_to_add = 12
                    missing_times = 0

                    if months_to_add:
                        missing_times = int(days_calculate_missing_invoices / (months_to_add * 30))
                    if tenant_db.exp_date:
                        # print("Email invoice ::::::::::::::::::::::::::::::::::::::::::::::::::::",tenant_db.exp_date,tenant_db.name)
                        for i in range(missing_times - 1):  # next_invoice_create_date < today:
                            print(5555555555555555555)
                            move_id = tenant_db._make_invoice()
                            if move_id:
                                # move invoice in "Open" state
                                if move_id.invoice_line_ids: move_id._auto_open_invoice()

                # =======================End=================================
            if tenant_db.expired:
                ##data purge email
                purge_date = str(datetime.datetime.strptime(str(tenant_db.exp_date), '%Y-%m-%d') + datetime.timedelta(days=grace_days + purge_days))[
                             :10]
                purge_date = purge_date.split('-')
                
                
                # print("purge_date::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",purge_date,tenant_db.name)
                y = purge_date[0]
                m = purge_date[1]
                d = purge_date[2]
                purge_date = datetime.datetime.strptime(d + '' + m + '' + y, '%d%m%Y').date()
                if (str(purge_date) == str(today)):
                    stage_ids = self.env['tenant.database.stage'].search([('is_purge', '=', True)])
                    tenant_db.write({'stage_id': stage_ids.id if stage_ids else False})
                    tenant_db.send_saas_alert_email('ready_for_purge')

        _logger.info('SaaS-Db Expire db check end')
        return True

    def _get_grace_period_date(self):
        """
        Get grace period expiration date of the agreement.
        """
        for tenant_db in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            grace_days = int(ICPSudo.search([('key', '=', 'grace_period')]).value)
            self.grace_period_date = str(datetime.datetime.strptime(str(tenant_db.exp_date), '%Y-%m-%d') + datetime.timedelta(days=int(grace_days)))[
                                     :10]
        return True

    @api.model
    def create(self, vals):
        print("vaaaaaaaaaaaaaaaaaa@@@@@1", vals)
        if 'invoice_term_id' in vals:
            del vals['invoice_term_id']
            if 'free_trial' in vals and vals['free_trial']:
                vals['next_invoice_create_date'] = vals['exp_date']
            return super(tenant_database_list, self).create(vals)

    def get_tenant_url(self):
        for o in self:
            so = o.sale_order_ref
            if so:
                ICPSudo = self.env['ir.config_parameter'].sudo()
                domain = ICPSudo.search([('key', '=', 'domain_name')]).value
                if not domain.startswith('.'):
                    domain = '.' + domain

                o.tenant_url = "%s%s" % (so.instance_name, domain)

    name = fields.Char('DB Name', size=64, index=True)
    exp_date = fields.Date('Expiry Date')
    next_invoice_create_date = fields.Date('Next invoice create date')
    expired = fields.Boolean('Terminated / Deactivated')
    free_trial = fields.Boolean('Free Trial')
    sale_order_ref = fields.Many2one('sale.order', 'Sale Order Ref.')
    no_of_users = fields.Integer('No of Users')
    active = fields.Boolean('Active', default=True)
    grace_period_date = fields.Date(compute='_get_grace_period_date', string='Grace Period Date')
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    reason = fields.Text('Reason')
    deactivated_date = fields.Date('Deactivated Date')

    stage_id = fields.Many2one('tenant.database.stage', 'Stage', track_visibility='onchange', index=True,
                               domain="[]")
    color = fields.Integer('Color Index', default=0)
    user_login = fields.Char('User Login', size=64)
    user_pwd = fields.Char('User Password', size=64)
    super_user_login = fields.Char('Super User Login', size=64)
    super_user_pwd = fields.Char('Super User Password', size=64)

    tenant_url = fields.Char(compute='get_tenant_url', string='Tenant URL')

    user_history_ids = fields.One2many('user.history', 'tenant_id', string="Users History")




class UserHistory(models.Model):
    _name = 'user.history'
    _description = 'User History'

    rec_date = fields.Date("Date")
    pre_users = fields.Integer("Previous Count")
    adding = fields.Integer("TO add")
    total = fields.Integer("Current Total")
    tenant_id = fields.Many2one('tenant.database.list', string='Tenant')
