from odoo import api, fields, models 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp
import odoo.netsvc


class recurring_term(models.Model):
    
    _name = 'recurring.term'
    _description = 'Recurring Term'
    
    
    
    name = fields.Char('Name', size=64, required=True)
    type = fields.Selection([('from_first_date','Monthly') ,('quarter','Quarterly'), ('half_year','Half Yearly') ,('year','Yearly')], 'Agreement term', default='from_first_date', required=True )
    active = fields.Boolean(default=True, string='Active')
    sequence = fields.Integer('Sequence')
    
    _order = 'sequence'
    
    _sql_constraints = [
        ('term_uniq', 'unique(type)', 'Select Type is already exist!'),
    ]    
    
    
