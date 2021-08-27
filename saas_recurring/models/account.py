from odoo import api, fields, models 


class account_invoice(models.Model):
    
    _inherit="account.move"
    
    agreement_id=fields.Many2one('sale.recurring.orders.agreement', string='Agreements')
    
    










