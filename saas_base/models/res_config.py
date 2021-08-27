from odoo import models, fields, api
# from pragmatic_saas.saas_base.admin_user import ADMINUSER_ID
from odoo.exceptions import UserError
from odoo.tools import config
import odoo
# import openerp
from odoo import api, fields, models, tools, _

ADMINUSER_ID = 2


class saas_config_setting(models.TransientModel):
    """ Setting days before to email alert """

    _inherit = 'res.config.settings'
    # _name = 'res.config.settings'
    _description = 'email alert before day'

    free_trail_no_of_days = fields.Integer(' Alert before No. Of Days (for Free Trial)')
    db_expire_no_of_days = fields.Integer('Alert before No. Of Days (for Database Expiration)')
    grace_period = fields.Integer('Grace Period for Pay Invoice(after Expiry)')
    free_trial_days = fields.Integer('Free Trial Period(days)')
    data_purging_days = fields.Integer('Data Purging Days(after Grace Period)')
    admin_pwd = fields.Char('Super Admin Password', size=64, required=True, help="admin login password for Tenant DB", default="admin")
    admin_login = fields.Char('Super Admin Login', required=True, size=64, help="Super Admin login for Tenant DB. \nDefault will be 'admin'")
    billing = fields.Selection([('normal', 'Per Module/Per Month')], string="Billing Type", default="normal")

    bare_tenant_db = fields.Char('Bare Tenant DB', size=200, help="Bare Tenant DB")
    brand_name = fields.Char('Brand Name', size=64)
    domain_name = fields.Char('Domain Name', size=64)
    brand_website = fields.Char('Brand Website', size=64)
    tenant_logo = fields.Binary('Tenant Database Logo [.png only]')
    favicon_logo = fields.Binary('Favicon Logo [.ico only]')
    filename_logo = fields.Char('Logo File Name')
    filename_fevicon = fields.Char('File Name ')
    payment_acquire = fields.Many2one('payment.acquirer', string='Payment Method For trial Period', default=5)

    # _defaults={
    #            'admin_pwd':'admin',
    #            'billing': 'normal',
    #            'admin_pwd':'admin',
    #            'brand_name': config.get('brand_name') if config and config.get('brand_name') else '',
    #            'brand_website' : config.get('brand_website') if config and config.get('brand_website') else '',
    #            'bare_tenant_db' : config.get('bare_db') if config and config.get('bare_db') else '',
    #            'free_trail_no_of_days':7,
    #            'db_expire_no_of_days':7,
    #            'grace_period':7,
    #            'free_trial_days':15,
    #            'data_purging_days':7
    #
    #            }

    @api.model
    def default_get(self, fields_list):
        res = super(saas_config_setting, self).default_get(fields_list)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        values = {
            'brand_name': ICPSudo.search([('key', '=', 'brand_name')]).value,
            'domain_name': ICPSudo.search([('key', '=', 'domain_name')]).value,
            'brand_website': ICPSudo.search([('key', '=', 'brand_website')]).value,
            'admin_login': ICPSudo.search([('key', '=', 'admin_login')]).value,
            'admin_pwd': ICPSudo.search([('key', '=', 'admin_pwd')]).value,
            'free_trail_no_of_days': int(ICPSudo.search([('key', '=', 'free_trail_no_of_days')]).value),
            'db_expire_no_of_days': int(ICPSudo.search([('key', '=', 'db_expire_no_of_days')]).value),
            'grace_period': int(ICPSudo.search([('key', '=', 'grace_period')]).value),
            'free_trial_days': int(ICPSudo.search([('key', '=', 'free_trial_days')]).value),
            'payment_acquire': int(ICPSudo.search([('key', '=', 'payment_acquire')]).value),
            'data_purging_days': int(ICPSudo.search([('key', '=', 'data_purging_days')]).value),
            'billing': ICPSudo.search([('key', '=', 'billing')]).value,
            'bare_tenant_db': ICPSudo.search([('key', '=', 'bare_tenant_db')]).value,
        }
        if not values['admin_pwd']:
            values['admin_pwd'] = 'admin'
        res.update(values)

        return res

    def set_favicon_logo(self, value):
        if not self.favicon_logo:
            return True

        if self.filename_fevicon:
            file_name = str(self.filename_fevicon)
            file_name = file_name.split('.')[-1]
            if file_name not in ['ico', "ICO"]:
                raise UserError("Favicon Logo image must be of .ico type")

        # Take addons path present at outside of openerp folder to set image path
        import os
        import shutil
        import base64
        path = ''
        paths = config.get('addons_path').split(',')
        for item in paths:
            if os.path.isfile(str(item) + '/web/static/src/img/favicon.ico'):
                path = str(item)
        # ------------End---------------------------
        if value:
            if not os.path.isfile(path + "/web/static/src/img/favicon_copy.ico"):
                shutil.copy2(path + '/web/static/src/img/favicon.ico', path + '/web/static/src/img/favicon_copy.ico')
            f1 = open(path + "/web/static/src/img/favicon.ico", "wb")

            f1.write(base64.b64decode(value + b'==='))
            f1.close

    def decode_base64(self, data, altchars=b'+/'):
        """Decode base64, padding being optional.
    
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
    
        """
        import base64
        import re
        data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
        missing_padding = len(data) % 4
        if missing_padding:
            data += b'=' * (4 - missing_padding)
        return base64.b64decode(data, altchars)

    def set_company_logo(self, value):
        if not self.tenant_logo:
            return True

        if self.filename_logo:
            file_name = str(self.filename_logo)
            file_name = file_name.split('.')[-1]
            if file_name not in ['png', "PNG"]:
                raise UserError("Tenant Database Logo image must be of .png type")

        import base64
        self.env['res.users'].browse(self.env.uid).company_id.write({'logo': value})
        path = ''
        paths = config.get('addons_path').split(',')
        import os.path
        for item in paths:
            if os.path.isdir(str(item) + '/base/static/img'):
                path = str(item)

        import os
        print(type(self.decode_base64(self.env['res.users'].browse(self.env.uid).company_id.logo)))

        try:
            os.remove(path + "/base/static/img/res_company_logo.png")
        except:
            print("path::::::::::;", path + "/base/static/img/res_company_logo.png")

        value2 = value.decode("utf-8")
        if len(value2) % 4:
            # not a multiple of 4, add padding:
            value2 += '=' * (4 - len(value2) % 4)

        value2 = value2.encode("utf-8")

        f3 = open(path + "/base/static/img/res_company_logo.png", "w+b")
        # f3.write(self.env['res.users'].browse(self.env.uid).company_id.logo)
        print("fffffffffffffffff", value2)
        f3.write(base64.b64decode(value + b'==='))
        f3.close()

        # self.env['res.users'].browse(self.env.uid).company_id.partner_id.write({'image': value2})

    def get_values(self):
        res = super(saas_config_setting, self).get_values()
        # print ("get values, resssss=======",res)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            free_trail_no_of_days=ICPSudo.get_param('free_trail_no_of_days'),
            db_expire_no_of_days=ICPSudo.get_param('db_expire_no_of_days'),
            grace_period=ICPSudo.get_param('grace_period'),
            free_trial_days=ICPSudo.get_param('free_trial_days'),
            payment_acquire=ICPSudo.get_param('payment_acquire', default=5),
            data_purging_days=ICPSudo.get_param('data_purging_days'),
            admin_pwd=ICPSudo.get_param('admin_pwd', default=False),
            admin_login=ICPSudo.get_param('admin_login', default=False),
            billing=ICPSudo.get_param('billing'),
            bare_tenant_db=ICPSudo.get_param('bare_tenant_db'),

            brand_name=ICPSudo.get_param('brand_name') or '',
            domain_name=ICPSudo.get_param('domain_name') or '',
            brand_website=ICPSudo.get_param('brand_website') or '',
            tenant_logo=ICPSudo.get_param('tenant_logo'),
            favicon_logo=ICPSudo.get_param('favicon_logo'),
        )
        # print("\n \n updated res",res)
        return res

    def set_configs(self, key, value):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if not ICPSudo.search([('key', "=", key)]) and value:
            ICPSudo.create({'key': key, 'value': value})
        else:
            if value:
                ICPSudo.search([('key', "=", key)]).write({'key': key, 'value': value})
            else:
                ICPSudo.search([('key', "=", key)]).unlink()
                return True

        if key == 'favicon_logo':
            self.set_favicon_logo(value)

        if key == 'tenant_logo':
            self.set_company_logo(value)

        return True

    def set_values(self):
        res=super(saas_config_setting, self).set_values()
        # print("set values, res =========", res)
        ICPSudo = self.env['ir.config_parameter'].sudo()



        self.set_configs('brand_name', self.brand_name or 'test')
        self.set_configs('domain_name', self.domain_name or 'test.domain')
        self.set_configs('brand_website', self.brand_website or 'test.domain.com')
        self.set_configs('admin_login', self.admin_login or 'admin')
        self.set_configs('admin_pwd', self.admin_pwd or 'admin')
        self.set_configs('free_trail_no_of_days', self.free_trail_no_of_days or 0)
        self.set_configs('db_expire_no_of_days', self.db_expire_no_of_days or 0)
        self.set_configs('grace_period', self.grace_period or 0)
        self.set_configs('free_trial_days', self.free_trial_days or 0)
        self.set_configs('payment_acquire', int(self.payment_acquire.id) or 5)
        self.set_configs('data_purging_days', self.data_purging_days or 0)
        self.set_configs('billing', self.billing or 'normal')
        self.set_configs('bare_tenant_db', self.bare_tenant_db or 'bare_tenant_13')
        self.set_configs('tenant_logo', self.tenant_logo)
        self.set_configs('favicon_logo', self.favicon_logo)


        if self.free_trial_days > 0:
            if not self.payment_acquire:
                raise UserError("Please Set Payment Acquire For Trial period")


        for record in self:
            ICPSudo.set_param("mail.catchall.pwd", record.admin_pwd or '')
            db_ids = [i.id for i in self.env["tenant.database.list"].search([])]
            for db in self.env["tenant.database.list"].browse(db_ids):
                print("record.admin_pwd::::::::::::::",record.admin_pwd)
                try:
                    registry = odoo.registry(db.name)
                    with registry.cursor() as tenant_cr:
                        tenant_env = odoo.api.Environment(tenant_cr, ADMINUSER_ID, {})
                        ret = tenant_env['res.users'].browse(2).write(
                            {'password': record.admin_pwd or 'admin', 'login': record.admin_login or 'admin'})
                except:
                    print('Some error, updating the tenant SuperUser login/password--------------')

        return res

        # ICPSudo.set_param('free_trail_no_of_days', self.free_trail_no_of_days)
        # ICPSudo.set_param("db_expire_no_of_days", self.db_expire_no_of_days)
        # ICPSudo.set_param("grace_period", self.grace_period)
        # ICPSudo.set_param("free_trial_days", self.free_trial_days)
        # ICPSudo.set_param('data_purging_days', self.data_purging_days)
        # ICPSudo.set_param('admin_pwd', self.admin_pwd)
        # ICPSudo.set_param('admin_login', self.admin_login)
        #
        # ICPSudo.set_param("billing", self.billing)
        # ICPSudo.set_param("bare_tenant_db", self.bare_tenant_db)
        # ICPSudo.set_param("brand_name", self.brand_name)
        # ICPSudo.set_param("domain_name", self.domain_name)
        # ICPSudo.set_param('brand_website', self.brand_website)
        # ICPSudo.set_param('tenant_logo', self.tenant_logo)
        # ICPSudo.set_param('favicon_logo', self.favicon_logo)


    # def set_admin_pwd(self):
    #
    #     config_parameters = self.env["ir.config_parameter"]
    #     for record in self:
    #         config_parameters.set_param("mail.catchall.pwd", record.admin_pwd or '')
    #         db_ids=[i.id for i in self.env["tenant.database.list"].search([])]
    #         for db in self.env["tenant.database.list"].browse(db_ids):
    #             client = erppeek.Client('http://localhost:1999', db.name, 'admin', 'admin')
    #             #===================================================================
    #             # Change admin password as per configured in Saas Configuration.
    #             #===================================================================
    #             try:
    #                 tenant_db = odoo.sql_db.db_connect(db.name)
    #                 tenant_cr=tenant_db.cursor()
    #                 tenant_cr = tenant_db.cursor()
    #                 client.model('res.users').browse(1).write({'password': record.admin_pwd or 'admin',
    #                                                                                 'login': record.admin_login or 'admin'})
    #                 tenant_cr.commit()
    #             except:print ('DB not Exist')
    #
    # @api.model
    # def set_admin_login(self):
    #     config_parameters = self.env["ir.config_parameter"]
    #     for record in self:
    #         config_parameters.set_param( "mail.catchall.login", record.admin_login or '')
    #         db_ids=[i.id for i in self.env["tenant.database.list"].search([])]
    #         for db in self.env["tenant.database.list"].browse():
    #             client = erppeek.Client('http://localhost:1999', db.name, 'admin', 'admin')
    #             tenant_db = odoo.sql_db.db_connect(db.name)
    #             tenant_cr=tenant_db.cursor()
    #             #===================================================================
    #             # Change admin login as per configured in Saas Configuration.
    #             #===================================================================
    #             try:
    #                 tenant_cr = tenant_db.cursor()
    #                 client.model('res.users').browse(1).write({'login': record.admin_login or 'admin'})
    #                 tenant_cr.commit()
    #             except:print ('DB not Exist')
    #
    #
    # @api.model
    # def set_billing(self):
    #     config_parameters = self.env["ir.config_parameter"]
    #     for record in self:
    #         config_parameters.set_param( "base_admin.billing", record.billing or '')



class WebsiteTrack(models.Model):
    _inherit = 'website.track'

    # @api.multi
    def update_existing_link(self):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if 'http://localhost:8069' in record.url:
                old_url = record.url
                new_url = old_url.replace("http://localhost:8069", base_url)
                record.url = new_url
