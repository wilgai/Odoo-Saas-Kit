from odoo import api, fields, models
from odoo import SUPERUSER_ID as ADMINUSER_ID

class product_template(models.Model):
    """ Inherited to add SAAS functionality"""
    
    _inherit = 'product.template'
    
    def _get_currency(self):
        """
        Get User Currency.
        """
#         if not ids: return {}
        result = {}
        for id in self:
            user = self
            result[id] = user.company_id.currency_id.symbol
        return result
    
    def _is_account_product(self):
        """
        Get User Currency.
        """
#         if not ids: return {}
        result = {}
        for id in self:
            product_obj = self.env['product.template']
            product = self
            result[id] = False
            print (result[id],'----')
            for module in product.product_tmpl_id.module_list:
                if module.name == 'account':
                    result[id] = True
        return result
    
    
    def _is_user_product(self):
        result = {}
        ICPSudo = self.env['ir.config_parameter'].sudo()
        buy_product = ICPSudo.search([('key', '=', 'buy_product')]).value
        setting_vals = self.env['res.config.settings'].default_get(  ['buy_product'] )
        if buy_product:
            product_id = int(buy_product)
            for id in self:
                result[id] = 0
                if int(product_id ) == id:
                    result[id] = 1
        return result
    
    
    def _get_trial_days(self):
        result = {}

        ICPSudo = self.env['ir.config_parameter'].sudo()
        free_trial_days = ICPSudo.search([('key', '=', 'free_trial_days')]).value
        if free_trial_days:
            days = free_trial_days
            for id in self:
                result[id] = days
        return result
    
    is_saas= fields.Boolean('SaaS Product')
    module_list= fields.Many2many('ir.module.module', 'product_template_module_rel', 'product_id', 'module_id', 'Module List')
#     saas_product_type= fields.Selection([('base','Base'), ('addon','Add Ons'), ('admin','Admin Use')], string='SaaS Product Type')
    user_product_check_price=fields.Integer(compute='_is_user_product', string='User Product Check')
    currency_symbol=fields.Char(compute='_get_currency', size=64, string='currency ')
    is_account_product=fields.Boolean(compute='_is_account_product', string='Account Product')
    trial_days=fields.Char(compute='_get_trial_days',  size=64, string='Trial Days')
    user_product = fields.Boolean("User Product")


class product_product(models.Model):
    """ Inherited to add SAAS functionality"""
    
#     def _get_saas_product_type(self):
#         #=======================================================================
#         # Method returns saas product type whether product is of type Addons OR Base type
#         #=======================================================================
#         res = {}
#         for o in self:
#             res[o.id] = o.product_tmpl_id.saas_product_type
#         return res
    
    _inherit = 'product.product'
#         'module_list' : fields.related('product_tmpl_id', 'module_list',
#                            type='many2many',
#                            relation='ir.module.module',
#                            string='Module List'),
    module_list=fields.Many2many('ir.module.module','ir_module_module_pro_rel','product_id','module_id')
    is_saas=fields.Boolean(related='product_tmpl_id.is_saas', string='SaaS Product')













