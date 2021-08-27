from odoo import api, fields, models, _
from odoo.exceptions import UserError

class user_aro(models.Model):
    
    _name = 'user.add.remove'
    _description = 'User Add Remove'
    
    tenant_id = fields.Many2one('tenant.database.list')
    total_users = fields.Integer()
    new_users = fields.Integer()
    log_date = fields.Date()
    type = fields.Selection([('add','Add') ,('remove','Remove')],default='add')


class ProductProduct(models.Model):
    _inherit='product.product'
    
    
    
    def get_list_price(self):
        
        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            pricelist = current_website.get_current_pricelist()
        
            prod_price = self.with_context(pricelist=pricelist.id).price
            return prod_price
        else:
            return self.lst_price
    
    def get_list_currency(self):
        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            pricelist = current_website.get_current_pricelist()
        
            return pricelist.currency_id.name if pricelist else self.currency_id.name
        else:
            return self.currency_id.name
    
        


 