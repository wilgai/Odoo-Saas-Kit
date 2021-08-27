# -*- encoding: utf-8 -*-


from odoo import api, fields, models 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp
import odoo

from odoo import netsvc 

class agreement_line(models.Model):

    _name = 'sale.recurring.orders.agreement.line'
    _description = 'Sale Recurring Order Agreement Line'
    
    
    active_chk = fields.Boolean('Active', help='Unchecking this field, this quota is not generated', default=1)
    agreement_id = fields.Many2one('sale.recurring.orders.agreement', string='Agreement reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', ondelete='set null')
    name = fields.Char('Description', size=128, help='Product description', required=True)
    quantity = fields.Float('Product quantity', required=True, help='Quantity of the product', default=1)
    price = fields.Float('Product price', digits='Sale Price', help='Specific price for this product. Keep empty to use the current price while generating order')
    discount = fields.Float('Discount (%)', digits=(16, 2))
    ordering_interval = fields.Integer('Order interval', default=1, help="Interval in time units for making and order of this product", required=True)
    ordering_unit = fields.Selection([('days', 'days'), ('weeks', 'weeks'), ('months', 'months'), ('years', 'years')], 'Ordering interval unit', default='months', required=True)
    last_order_date = fields.Date('Last order date')
    notes = fields.Char('Notes', size=300) 
    createdate = fields.Date('Create Date')

#     _defaults = {
#         'active_chk': lambda *a: 1,
#         'quantity': lambda *a: 1,
#         'ordering_interval': lambda *a: 1,
#         'ordering_unit': lambda *a: 'months',
#     }
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if self.product_id:
#             product = self.env['product.product'].browse(self.product_id)
            result['value'] = { 'name': self.product_id['name'] }
        return result

agreement_line()



class agreement(models.Model):
    
    
#     def active_inactive_toggle(self, cr, uid, ids, conText={}):
#         isactive = self.browse(cr, uid, ids)[0].active
#         if isactive == True:
#             self.write(cr, uid, ids,{'active':False})
#         else:
#             self.write(cr, uid, ids,{'active':True})
    def active_inactive_toggle(self):
        isactive = self.active
        if isactive == True:
            self.write({'active':False})
        else:
            self.write({'active':True})
        
        
        
    def __get_next_term_date(self, date, unit, interval):
        """
        Get the date that results on incrementing given date an interval of time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.    
        """
        if unit == 'days':
            return date + timedelta(days=interval)
        elif unit == 'weeks':
            return date + timedelta(weeks=interval)
        elif unit == 'months':
            return date + relativedelta(months=interval)
        elif unit == 'years':
            return date + relativedelta(years=interval)
      
#     def _get_instance_name(self, cr, uid, ids, field_name, arg, conText=None):
#         """
#         Get instance name of the agreement.
#         """
#         if not ids: return {}
#         res = {}
#         for agreement in self.browse(cr, uid, ids):
#             res[agreement.id] = ''
#             for agreement_sale_order in agreement.order_line:
#                 res[agreement.id] = agreement_sale_order.order_id.instance_name
#                 break
#         return res
    def _get_instance_name(self):
        """
        Get instance name of the agreement.
        """
        if not self._ids: return {}
        res = {}
        for agreement in self:
            res[agreement.id] = ''
            for agreement_sale_order in agreement.order_line:
                res[agreement.id] = agreement_sale_order.order_id.instance_name
                break
        return res
    
#     def _get_current_users(self, cr, uid, ids, field_name, arg, conText=None):
#         """
#         Get count of current users of the agreement.
#         """
#         if not ids: return {}
#         res = {}
#         for agreement in self.browse(cr, uid, ids):
#             res[agreement.id] = 0
#             db_ids = self.pool.get('tenant.database.list').search(cr, uid, [('name', '=', agreement.instance_name)])
#             if db_ids:
#                 res[agreement.id] = self.pool.get('tenant.database.list').browse(cr, uid, db_ids[0]).no_of_users
#         return res


    
    def _get_current_users(self):
        """
        Get count of current users of the agreement.
        """
        for agreement in self:
            num = 1
            db_ids = self.env['tenant.database.list'].search([('name', '=', agreement.instance_name)])
            if db_ids:
#                 res[agreement.id] = self.env['tenant.database.list'].browse(db_ids[0]).no_of_users
        
                num = db_ids[0].no_of_users or 1
                
                
            print (num, 'num....................')
            
            agreement.current_users = str(num) 

#     def __get_next_expiration_date(self, cr, uid, ids, field_name, arg, conText=None):
#         """
#         Get next expiration date of the agreement. For unlimited agreements, get max date
#         """
#         if not ids: return {}
#         res = {}
#         for agreement in self.browse(cr, uid, ids):
#             res[agreement.id] = False
#             if agreement.prolong == 'fixed':
#                 res[agreement.id] = agreement.end_date
#             elif agreement.prolong == 'unlimited':
#                 now = datetime.now()
#                 date = self.__get_next_term_date(datetime.strptime(agreement.start_date, "%Y-%m-%d"), agreement.prolong_unit, agreement.prolong_interval)
#                 while (date < now):
#                     date = self.__get_next_term_date(date, agreement.prolong_unit, agreement.prolong_interval)
#                 res[agreement.id] = date
#             else:
#                 # for renewable fixed term
#                 res[agreement.id] = self.__get_next_term_date(datetime.strptime( \
#                     agreement.last_renovation_date if agreement.last_renovation_date else agreement.start_date, "%Y-%m-%d"), \
#                     agreement.prolong_unit, agreement.prolong_interval)
#         return res
    def __get_next_expiration_date(self):
        """
        Get next expiration date of the agreement. For unlimited agreements, get max date 
        """
        if not self._ids: return {}
        res = {}
        for agreement in self:
            res[agreement.id] = False
            if agreement.prolong == 'fixed':
                res[agreement.id] = agreement.end_date
            elif agreement.prolong == 'unlimited':
                now = datetime.now()
                date = self.__get_next_term_date(datetime.strptime(agreement.start_date, "%Y-%m-%d"), agreement.prolong_unit, agreement.prolong_interval)
                while (date < now):
                    date = self.__get_next_term_date(date, agreement.prolong_unit, agreement.prolong_interval)
                res[agreement.id] = date
            else:
                # for renewable fixed term
                res[agreement.id] = self.__get_next_term_date(datetime.strptime(\
                    agreement.last_renovation_date if agreement.last_renovation_date else agreement.start_date, "%Y-%m-%d"), \
                    agreement.prolong_unit, agreement.prolong_interval)
        return res

    _name = 'sale.recurring.orders.agreement'
    _description = 'Sale Recurring Orders Agreement'
    
    
    name = fields.Char('Name', size=100, index=1, required=True, help='Name that helps to identify the agreement', default=1)
    number = fields.Char('Agreement No', index=1, size=32, help="Number of agreement. Keep empty to get the number assigned by a sequence.")
    active = fields.Boolean('Active', help='Unchecking this field, quotas are not generated')
    partner_id = fields.Many2one('res.partner', 'Customer', index=1, change_default=True, required=True, help="Customer you are making the agreement with")
    company_id = fields.Many2one('res.company', 'Company', required=True, help="Company that signs the agreement", default=lambda self: self.env['res.company']._company_default_get())
    start_date = fields.Date('Start date', index=1, help="Beginning of the agreement. Keep empty to use the current date")
    prolong = fields.Selection([('recurrent', 'Renewable fixed term'), ('unlimited', 'Unlimited term'), ('fixed', 'Fixed term')], 'Prolongation', default='unlimited', help="Sets the term of the agreement. 'Renewable fixed term=It sets a fixed term, but with possibility of manual renew; 'Unlimited term=Renew is made automatically; 'Fixed term=The term is fixed and there is no possibility to renew.", required=True)
    end_date = fields.Date('End date', help="End date of the agreement")
    prolong_interval = fields.Integer('Interval', default=1, help="Interval in time units to prolong the agreement until new renewable (that is automatic for unlimited term, manual for renewable fixed term).")
    prolong_unit = fields.Selection([('days', 'days'), ('weeks', 'weeks'), ('months', 'months'), ('years', 'years')], 'Interval unit', default='years', help='Time unit for the prolongation interval')
    agreement_line = fields.One2many('sale.recurring.orders.agreement.line', 'agreement_id', 'Agreement lines')
    order_line = fields.One2many('sale.recurring.orders.agreement.order', 'agreement_id', 'Order lines', readonly=True)
    invoice_ids = fields.One2many('account.move', 'agreement_id', 'Invoices', readonly=True)
    last_renovation_date = fields.Date('Last renovation date', help="Last date when agreement was renewed (same as start date if not renewed)")
    next_expiration_date = fields.Date(compute='__get_next_expiration_date', string='Contract Renewal Date', method=True, store=True)
    state = fields.Selection([('empty', 'Without orders') , ('first', 'First order created') , ('orders', 'With orders')], 'State', readonly=True)
    renewal_state = fields.Selection([('not_renewed', 'Agreement not renewed'), ('renewed', 'Agreement renewed')], 'Renewal state', default='not_renewed', readonly=True)
    notes = fields.Text('Notes')
    version_no = fields.Char('Version No.', size=50)
    log_history = fields.Text('Log History')
    invoice_term_id = fields.Many2one('recurring.term', 'Invoicing Term', required=True)
    instance_name = fields.Char(string='Instance Name', size=100)
    current_users = fields.Char(compute='_get_current_users', string='Current Users', size=100, store=False)



    _sql_constraints = [
        ('number_uniq', 'unique(number)', 'Agreement number must be unique !'),
    ]
    @api.constrains
    def _check_dates(self):
        """
        Check correct dates. When prolongation is unlimited or renewal, end_date is False, so doesn't apply
        @rtype: Boolean
        @return: True if dates are correct or don't apply, False otherwise
        """
        if self.end_date < self.start_date:
            UserWarning('1Agreement end date must be greater than start date')


        val = True
        for agreement in self:
            if agreement.end_date: val = val and agreement.end_date > agreement.start_date
        return val
    _constraints = [
        (_check_dates, 'Agreement end date must be greater than start date', ['start_date','end_date']),
    ]

    @api.model
    def create(self, vals):
        # Set start date if empty
        if not vals.get('start_date'): 
            vals['start_date'] = datetime.now()
        
        # Set agreement number if empty
        if not vals.get('number'): 
            vals['number'] = self.env['ir.sequence'].get('sale.r_o.agreement.sequence')
        vals['name'] = vals['number']
        res = super(agreement, self).create(vals)
        
        # Attach related invoice to the agreement  
        if 'instance_name' in vals:
            invoice_ids = self.env['account.move'].search([('name', '=', vals['instance_name']), ('agreement_id', '=', False)])
            invoice_ids.write({'agreement_id': res})
        return res

#     @api.model
    def write(self, vals):
        value = super(agreement, self).write(vals)
#         unlink all future orders
        if 'active' in vals or 'number' in vals or ('agreement_line' in vals and len(vals['agreement_line'])) \
            or 'prolong' in vals or 'end_date' in vals or 'prolong_interval' in vals or 'prolong_unit' in vals:
#             print ("selfffffffffffff of writwwee" ,self)
            self.unlink_orders(datetime.date(datetime.now()))
        return value
    
#     def copy(self, cr, uid, orig_id, default={}, conText=None):
#         if conText is None: conText = {}
#         agreement_record = self.browse(cr, uid, orig_id)
#         default.update({
#             'state': 'empty',
#             'number': False,
#             'active': True,
#             'name': '%s*' % agreement_record['name'],
#             'start_date': False,
#             'order_line': [],
#             'renewal_line': [],
#         })
#         return super(agreement, self).copy(cr, uid, orig_id, default, conText)
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default.update({
            'state': 'empty',
            'number': False,
            'active': True,
            'name': '%s*' % self['name'],
            'start_date': False,
            'order_line': [],
            'renewal_line': [],
        })
        return super(agreement, self).copy(default)

#     def onchange_start_date(self, cr, uid, ids, start_date=False):
#         """
#         It changes last renovation date to the new start date.
#         @rtype: dictionary
#         @return: field last_renovation_date with new start date
#         """
#         if not start_date: return {}
#         result = {}
#         result['value'] = { 'last_renovation_date': start_date }
#         return result
    @api.onchange('start_date')
    def onchange_start_date(self):
        """
        It changes last renovation date to the new start date.
        @rtype: dictionary
        @return: field last_renovation_date with new start date
        """
        if not self.start_date: return {}
        result = {}
        result['value'] = { 'last_renovation_date': self.start_date }
        return result


    def create_order(self, date, agreement_lines):
        """
        Method that creates an order from given data.
        @param agreement: Agreement method get data from.
        @param date: Date of created order.
        @param agreement_lines: Lines that will generate order lines.
        @confirmed_flag: Confirmed flag in agreement order line will be set to this value.   
        """
        order_obj = self.env['sale.order']
        order_line_obj = self.env['sale.order.line']
        # Create order object
        order = {
            'date_order': date.strftime('%Y-%m-%d'),
            'date_confirm': date.strftime('%Y-%m-%d'),
            'origin': self.number,
            'partner_id': self.partner_id.id,
            'state': 'draft',
            'company_id': self.env.user.company_id.id,
            'from_existed_agreement':True,
        }
        # Get other order values from agreement partner
        order.update(order_obj.onchange_partner_id(agreement.partner_id.id)['value'])                   
        order['user_id'] = agreement.partner_id.user_id.id
        order_id = order_obj.create(order)
        # Create order lines objects
        agreement_lines = []
        for agreement_line in agreement_lines:
            order_line = {
                'order_id': order_id,
                'product_id': agreement_line.product_id.id,
                'product_uom_qty': agreement_line.quantity,
                'discount': agreement_line.discount,
            }
            # get other order line values from agreement line product
            order_line.update(order_line_obj.product_id_change(order['pricelist_id'], \
                product=agreement_line.product_id.id, qty=agreement_line.quantity, partner_id=agreement.partner_id.id, \
                 fiscal_position=order['fiscal_position'] if 'fiscal_position' in order else False)['value'])
            if agreement_line.price > 0: order_line['price_unit'] = agreement_line.price
            # Put line taxes
            order_line['tax_id'] = [(6, 0, tuple(order_line['tax_id']))]
            # Put custom description
            order_line['name'] = '[%s] %s' % (agreement_line.product_id.default_code, agreement_line.name) 
            order_line_obj.create(order_line)
            agreement_lines.append(agreement_line)
        # Update last order date for lines
        for agreement_line in agreement_lines:
            agreement_line.write({'last_order_date': date.strftime('%Y-%m-%d')})
        # Update agreement state
        if self.state != 'orders':
            self.write({'state': 'orders'})
        # Create order agreement record
        agreement_order = {
            'agreement_id': agreement.id,
            'order_id': order_id,
            # 'confirmed': confirmed_flag,
        }
        #vishnu123456
        #self.env['sale.recurring.orders.agreement.order'].create(agreement_order)
        return order_id

    def _order_created(self, agreement, agreement_lines_ordered, order_id):
        """
        It triggers actions after order is created.
        This method can be overriden for extending its functionality thanks to its parameters.
        @param agreement: Agreement object whose order has been created
        @param agreement_lines_ordered: List of agreement lines objects used in the creation of the order.
        @param order_id: ID of the created order.  
        """
        pass
    

    def _order_confirmed(self,order_id):
        """
        It triggers actions after order is confirmed.
        This method can be overriden for extending its functionality thanks to its parameters.
        @param agreement: Agreement object whose order has been confirmed
        @param order_id: ID of the confirmed order.
        """
        pass
#     def _order_confirmed(self, order_id):
#         """
#         It triggers actions after order is confirmed.
#         This method can be overriden for extending its functionality thanks to its parameters.
#         @param agreement: Agreement object whose order has been confirmed
#         @param order_id: ID of the confirmed order.
#         """
#         pass

#     def _get_next_order_date(self, agreement, line, startDate, conText={}):
#         """
#         Get next date starting from given date when an order is generated.
#         @param line: Agreement line  
#         @param startDate: Start date from which next order date is calculated.
#         @rtype: datetime
#         @return: Next order date starting from the given date.  
#         """
#         next_date = datetime.strptime(agreement.start_date, '%Y-%m-%d')
#         while next_date <= startDate:
#             next_date = self.__get_next_term_date(next_date, line.ordering_unit, line.ordering_interval)
#         return next_date
    def _get_next_order_date(self, line, startDate):
        """
        Get next date starting from given date when an order is generated.
        @param line: Agreement line  
        @param startDate: Start date from which next order date is calculated.
        @rtype: datetime
        @return: Next order date starting from the given date.  
        """
        next_date = datetime.strptime(agreement.start_date, '%Y-%m-%d')
        while next_date <= startDate:
            next_date = self.__get_next_term_date(next_date, line.ordering_unit, line.ordering_interval)
        return next_date

    def generate_agreement_orders(self, startDate, endDate):
        """
        Check if there is any pending order to create for given agreement. 
        """
        print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXgenerate_agreement_orders')
        if not self.active:
            return
        lines_to_order = {}
        agreement_expiration_date = datetime.strptime(self.next_expiration_date, '%Y-%m-%d') 
        if (agreement_expiration_date < endDate) and (self.prolong != 'unlimited'):
            endDate = agreement_expiration_date 
        for line in self.agreement_line:
            # Check if there is any agreement line to order 
            if line.active_chk:
                # Check future orders for this lineuntil endDate
                next_order_date = self._get_next_order_date(line, startDate)
                while next_order_date <= endDate:
                    # Add to a list to order all lines together
                    if not lines_to_order.get(next_order_date):
                        lines_to_order[next_order_date] = []
                    lines_to_order[next_order_date].append(line)
                    next_order_date = self._get_next_order_date(line, next_order_date)
        # Order all pending lines
        dates = lines_to_order.keys()
        dates.sort()
        agreement_order_obj = self.env['sale.recurring.orders.agreement.order']
        for date in dates: 
            # Check if an order exists for that date
            agreement_ids = agreement_order_obj.sudo().search([('date', '=', str(date.date())), ('agreement_id', '=', self['id'])])
            if not agreement_ids:
                # create it if not exists
                ############ How to check parameterssssssss //priya
                order_id = self.create_order(agreement, date, lines_to_order[date], False)
                # Call 'event' method
                self._order_created(agreement, lines_to_order, order_id)

#     def generate_initial_order(self):
#         """
#         Method that creates an initial order with all the agreement lines
#         """
#         agreement_lines = []
#         # Add only active lines
#         for line in self.agreement_line:
#             if line.active_chk: agreement_lines.append(line)
#         order_id = self.create_order(agreement, datetime.strptime(agreement.start_date, '%Y-%m-%d'), agreement_lines, True)
#         # Update agreement state
#         self.write({ 'state': 'first' })
#         # Confirm order
#         odoo.LocalService.trg_validate('sale.order', order_id, 'order_confirm')
#         # Get view to show
#         data_obj = self.env['ir.model.data']
#         result = data_obj._get_id('sale', 'view_order_form')
#         view_id = data_obj.browse(result).res_id
#         # Return view with order created
#         return {
#             'domain': "[('id','=', " + str(order_id) + ")]",
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'sale.order',
#             'conText': self._context,
#             'res_id': order_id,
#             'view_id': [view_id],
#             'type': 'ir.actions.act_window',
#             'nodestroy': True
#         }

    def generate_next_year_orders(self):
        """
        Method that generates all the orders of the given agreements for the next year, counting from current date.
        """
        startDate = datetime.now()
        endDate = datetime(startDate.year + 1, startDate.month, startDate.day) 
        for agreement in self:
            agreement.generate_agreement_orders(startDate, endDate)
        return True
    
    

    def unlink_orders(self, startDate):
        """
        Remove generated orders from given date.
        """
        agreement_order_obj = self.env['sale.recurring.orders.agreement.order'].sudo()
        ordersToRemove = []
        for agreement in self:
            for order in agreement['order_line']:
#                 print("order['date']==============",order['date'],type(order['date']))
                order_date = order['date'].date()
                if order_date > startDate:
                    if order['order_id']['id']: ordersToRemove.append(order['order_id']['id'])
#                     print ("====================   ",order['id'])
                    order['id'].unlink()                    
        print ("ordersToRemove    ",ordersToRemove)
        ordersToRemove
        
agreement()



#TODO: Impedir que se haga doble clic sobre el registro order
class agreement_order(models.Model):
    """
    Class for recording each order created for each line of the agreement. It keeps only reference to the agreement, not to the line.
    """
    


    def get_confirm_state(self):
        """
        Get confirmed state of the order.
        """
        for agreement_order in self:
            agreement1 = self.env['sale.recurring.orders.agreement.order'].sudo().search([])
            if agreement_order.order_id:
                agreement1.confirmed = agreement_order.order_id.state != 'draft'
                
                

    _name = 'sale.recurring.orders.agreement.order'
    _description = 'Sale Recurring Orders Agreement Order'
    
    agreement_id= fields.Many2one('sale.recurring.orders.agreement', string='Agreement reference', ondelete='cascade')
    order_id= fields.Many2one('sale.order', 'Order', ondelete='cascade')
    date= fields.Datetime(related='order_id.date_order', string="Order date", store=False)
    confirmed= fields.Boolean(compute='get_confirm_state', string='Confirmed',  method=True, store=False)

    def view_order(self):
        """
        Method for viewing orders associated to an agreement
        """
        order_id = self.order_id.id
        # Get view to show
        data_obj = self.env['ir.model.data']
        result = data_obj._get_id('sale', 'view_order_form')
        view_id = data_obj.browse(result).res_id
        # Return view with order created
        return {
            # 'domain': "[('id','=', " + str(order_id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'conText': self._context,
            'res_id': order_id,
            'view_id': [view_id],
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }



