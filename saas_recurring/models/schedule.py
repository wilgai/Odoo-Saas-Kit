from odoo import api, fields, models 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp
import odoo.netsvc

class agreement_schedule(models.Model):
    _name = 'agreement.schedule'
    _description = 'Agreement Schedule'
    
    
    
    
    def run_scheduler_of_invoice(self):
        """
        This scheduler method will execute every day to process agreements, i.e. to make invoices of agreements.
        that satisfy following conditions
        """
        conText=self._context
        print("run::::::::::::::::::::::::::::")
        if conText is None:
            conText={}

        today = datetime.now().day
        current_year = datetime.now().year
        current_month = datetime.now().month

        sale_reccuring_obj = self.env['sale.recurring.orders.agreement'].sudo()
        print("sale_reccuring_obj:::::::::",sale_reccuring_obj,today,current_year,current_month)
        recurring_term_obj = self.env['recurring.term']
        invoice_obj = self.env['account.move']

        flag_continue = False
        agreement_term_id = recurring_term_obj.search([('active', '=', True)])
        if agreement_term_id:
            term_type = agreement_term_id[0].type

            agreement_ids = sale_reccuring_obj.search([])
            if agreement_ids and agreement_term_id:
                for agreement in agreement_ids:
                    for order in agreement.order_line:
                        flag_continue = False

                        #===============================================================
                        # To find journal_id
                        #===============================================================
                        company_id = self.env.user.company_id.id
                        res = self.env['account.journal'].search([('type', '=', 'sale'),('company_id', '=', company_id)],limit=1)

                        journal_id =  res and res[0] or False

                        sale_order_id = order.order_id.id
                        order_date = order.date
                        chunk_list = str(order_date).split('-')
                        year = chunk_list[0]
                        if str(current_year) == year:

                            #=======================================================
                            # If term selected is 'daily'.
                            # If term selected is 'from_first_date' and current
                            # date is 1 i.e. first date of month.
                            #=======================================================
                            if term_type == 'daily' or (term_type == 'from_first_date' and today == 1):
                                flag_continue = True



                            #=======================================================
                            # If term selected is 'from_so_date' check whether
                            # current month is greater than SO date month by 1.
                            #=======================================================
                            if term_type == 'from_so_date':
                                if int(chunk_list[1]) < 12 and current_month > int(chunk_list[1]):
                                    flag_continue = True
                                elif int(chunk_list[1]) == 12 and current_month != 12:
                                    flag_continue = True

                            if flag_continue:
                                sale_order_obj = self.env['sale.order'].browse(sale_order_id)
                                account_id = sale_order_obj.partner_id.property_account_receivable_id.id
                                invoice_vals = {
                                                'name': sale_order_obj.name,
                                                'type': 'out_invoice',
                                               'invoice_origin': sale_order_obj.name,
                                                #'comment': 'Recurring invoice',
                                                'invoice_date': sale_order_obj.date_order,
                                               'invoice_user_id': self.env.user.id,
                                                'partner_id':sale_order_obj.partner_id.id,
                                                # 'account_id':account_id,
                                                'journal_id':journal_id.id,
                                                # 'sale_order_ids': [(4,sale_order_obj.id)],
                                                'invoice_line_ids': [
                                                    (0, 0, {
                                                            'name': sale_order_obj.order_line.product_id.name,
                                                            'product_id': sale_order_obj.order_line.product_id.id,
                                                            'product_uom_id': sale_order_obj.order_line.product_id.uom_id.id,
                                                            'price_unit': sale_order_obj.order_line.price_unit,
                                                            'tax_ids': [(6, 0, sale_order_obj.order_line.tax_id.ids)],
                                                            # 'invoice_line_tax_ids': [
                                                            # [6, False, [sale_order_obj.order_line.product_id.taxes_id.id]]]
                                                        # 'analytic_tag_ids': [(6, 0, sale_order_objorder_line.analytic_tag_ids.ids)],

                                        })],
                                                 }




                                # for line in sale_order_obj.order_line:
                                #     invoice_line_vals = {
                                #         'name': line.product_id.name,
                                #         'price_unit': line.price_unit,
                                #         'price_unit_show': line.product_id.lst_price,
                                #         'quantity': 1,
                                #         'product_id': line.product_id.id,
                                #         'product_uom_id': line.product_id.uom_id.id,
                                #         # 'price_subtotal': line.product_id.lst_price * months * self.sale_order_ref.no_of_users,
                                #         # 'tax_ids': [(6, 0, so_line.tax_id.ids)],
                                #         # 'sale_line_ids': [(6, 0, [so_line.id])],
                                #         # 'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                                #         'analytic_account_id': False,
                                #         # 'invoice_line_tax_ids':[[6, False, [line.product_id.taxes_id.id]]]
                                #     }
                                #
                                #
                                # invoice_vals['invoice_line_tax_ids'].append((0, 0, [sale_order_obj.order_line.product_id.taxes_id.id]))

                                    # if line.product_id.taxes_id.id:
                                    #     invoice_line_vals['invoice_line_tax_ids'] = [[6, False, [line.product_id.taxes_id.id]]] #[(6, 0, [line.product_id.taxes_id.id])],

                                inv = invoice_obj.create(invoice_vals)
                                sequence = inv._get_sequence()
                                name1 = sequence.next_by_id(sequence_date=inv.date)
                                inv.name = name1

        return True
#
#













