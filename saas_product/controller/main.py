from odoo import http, fields
from odoo.http import request
import werkzeug
try:
    from odoo.addons.website_sale.controllers.main import WebsiteSale
except:
    from addons.website_sale.controllers.main import WebsiteSale
from odoo import models, api
from odoo.addons.website.controllers.main import Website
import json
import odoo
import datetime
import time
from odoo.addons.payment.controllers.portal import PaymentProcessing
import xmlrpc
import logging
from odoo.exceptions import UserError




_logger = logging.getLogger(__name__)
class saas_pro(http.Controller):

    @http.route('/apps', auth='public', website=True)
    def saas_index(self, **kw):
        user = ''
        if request.session.uid:
            user = request.session.uid
            user = request.env['res.users'].sudo().search([('id', '=', user)])
        product_list = request.env['product.product'].sudo().search([('product_tmpl_id.is_saas', '=', True), ('website_published', '=', True)])
        active = ''
        if user:
            active = request.env['tenant.database.list'].sudo().search([('stage_id', '=', 1), ('user_login', '=', user.login)])
            if not active:
                active = request.env['tenant.database.list'].sudo().search([('stage_id', '=', 1), ('user_login', '=', user.partner_id.email)])
        # active = request.env['tenant.database.list'].sudo().search([('stage_id','=',1)])
        # print("\n\n\n\n\n\n ",active[1].sale_order_ref.order_line)
        return request.render('saas_product.saas_index', {
            'product': product_list, 'tenant': active
        })

    # @http.route('/apps/db_details/add_user' , auth='public', website=True)
    # def saas_add_users(self, **kw):
    #     print("\n\n\n\n\n  **KW :::: ",kw)
    #     product_list = request.env['product.product'].search([('is_saas','=',True)])
    #     return request.render('saas_product.saas_index', {
    #         'product':product_list
    #         })

    @http.route('/apps/dbs', auth='public', website=True)
    def show_dbs(self, **kw):
        # print("\n\n\n\n\n",request.session,"\n\n\n\n")
        # in_active = request.env['tenant.database.list'].sudo().search([('stage_id','=',4)])
        # active = request.env['tenant.database.list'].sudo().search([('stage_id','=',1)])
        # terminated = request.env['tenant.database.list'].sudo().search([('stage_id','=',5)])
        user = False
        if request.session.uid:
            user = request.session.uid
            user = request.env['res.users'].sudo().search([('id', '=', user)])
        print(user, 'User ======1234', user.login)
        active_id = request.env['tenant.database.stage'].sudo().search([('is_active', '=', True)], limit=1)
        inactive_id = request.env['tenant.database.stage'].sudo().search([('is_expired', '=', True)], limit=1)
        terminated_id = request.env['tenant.database.stage'].sudo().search([('is_purge', '=', True)], limit=1)

        print(active_id, inactive_id, terminated_id, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

        in_active = request.env['tenant.database.list'].sudo().search([('stage_id', '=', inactive_id.id), ('user_login', '=', user.login)])
        active = request.env['tenant.database.list'].sudo().search([('stage_id', '=', active_id.id), ('user_login', '=', user.login)])
        terminated = request.env['tenant.database.list'].sudo().search([('stage_id', '=', terminated_id.id), ('user_login', '=', user.login)])
        print(in_active, active, terminated, 'TTTTTTTTTTTTTTTTTT')
        return request.render('saas_product.saas_dbs', {
            'in_active': in_active,
            'active': active,
            'terminated': terminated
        })

    @http.route('/apps/db_details', auth='public', website=True)
    def db_details(self, **kw):
        user = False
        if request.session.uid:
            user = request.session.uid
            user = request.env['res.users'].sudo().search([('id', '=', user)])

        print("\n \n ", kw, request._context)
        tenant = request.env['tenant.database.list'].sudo().search([('id', '=', kw.get('id'))])
        print("\n\n\n\n\n in db_details", tenant, " \n\n\n\n\n")
        # return json.dumps(tenant.id)
        registry = odoo.registry(tenant.name)
        users = []
        users_inactive = []
        with registry.cursor() as tenant_cr:
            tenant_env = odoo.api.Environment(tenant_cr, 1, {})
            main_tenant_user = tenant_env['res.users'].sudo().search([('tenant_user', '=', True)],limit=1)
            active_domain = []
            inactive_domain = [('active', '=', False)]

            if main_tenant_user:
                active_domain.append(('id', '>=', main_tenant_user.id))
                inactive_domain.append(('id', '>=', main_tenant_user.id))

            tenant_users = tenant_env['res.users'].sudo().search(active_domain)
            for item in tenant_users:
                if item.tenant_user:
                    users.append({'name': item.name, 'login': item.login, 'sub_user': True})
                else:
                    users.append({'name': item.name, 'login': item.login, 'sub_user': False})

            tenant_users = tenant_env['res.users'].sudo().search(inactive_domain)
            for item in tenant_users:
                users_inactive.append({'name': item.name, 'login': item.login, 'sub_user': False})

            print(users_inactive, 'FFFFFFFFFFFFFFFFFFFFFFFFFFFF---', tenant)

        return request.render('saas_product.saas_tenants', {
            'tenant': tenant,
            'users': users,
            'users_inactive': users_inactive,
            'db': tenant.name,
        })

    def send_user_increase_mail(self,db_name,user_to_add):
        _logger.info("DATABSAE NAME  AND ADDING OF USERS IS ---> {} {}".format(db_name,user_to_add))
        template_id = request.env['ir.model.data'].get_object_reference('saas_product','saas_user_increase_notification_template')
        _logger.info("TEMPLATE ID IS ---> {}".format(template_id))
        email_temp_obj = request.env['mail.template'].sudo().browse(template_id)
        _logger.info("TEMPLATE OBJECT IS ---> {}".format(email_temp_obj))
        current_time = datetime.datetime.now().isoformat(' ', 'seconds')
        # post the message
        template = request.env.ref('saas_product.saas_user_increase_notification_template')
        _logger.info("TEMPLATE IS ---> {}".format(template))
        mail_server_attached = template.sudo().mail_server_id
        _logger.info("MAIL SERVER ATTACHED IS ---> {}".format(mail_server_attached))
        #Get the mail server object
        mail_server_object =  request.env['ir.mail_server'].sudo().search([('id','=',mail_server_attached.id)])
        _logger.info("MAIL SERVER OBJECT IS ---> {}".format(mail_server_object))
        template_subject = template.sudo().subject
        _logger.info("TEMPLATE SUBJECT IS ---> {}".format(template_subject))
        formatted_subject = template_subject.format(db_name)
        _logger.info("FORMATTED SUBJECT IS ---> {}".format(formatted_subject))
        template_body = template.sudo().body_html
        _logger.info("TEMPLATE BODY IS ---> {}".format(template_body))
        user_id = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        formatted_body = template_body.format(user_id.name,db_name,user_to_add,current_time)
        _logger.info("FORMATTED BODY IS ---> {}".format(formatted_body))
        mail_values = {
            'author_id' :3,
            'model': None,
            'res_id': None,
            'subject': formatted_subject,
            'body_html': formatted_body,
            'reply_to' : None
        }
        if mail_server_attached : 
            _logger.info("Mail server id is ---> {}".format(mail_server_attached.id))
            mail_values['mail_server_id'] = mail_server_attached.id
        if mail_server_object.smtp_user : 
            _logger.info("MAIL SERVER EMAIL ID IS ---> {}".format(mail_server_object.smtp_user))
            mail_values['email_from'] = mail_server_object.smtp_user
        return request.env['mail.mail'].sudo().create(mail_values)


    @http.route(['/apps/add_more_users'], type='http', auth="public", website=True, csrf=False)
    def add_more_users(self, **post):
        
        sum = False
        total_amount = 0
        invoice_amount = 0
        db_name = str(post['db']).split('|')
        if len(db_name) == 3:
            db_name = db_name[1]
        print('SUCESSSSSSSSSSSSSSSSSS', db_name)
        db_name = db_name.strip()
        user_to_add = post['users']
        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', db_name)])

        ICPSudo = request.env['ir.config_parameter'].sudo()
        buy_product_id = int(ICPSudo.search([('key', '=', 'buy_product')]).value or False)
        brand_website = ICPSudo.search([('key', '=', 'brand_website')]).value
        brand_admin = ICPSudo.search([('key', '=', 'admin_login')]).value
        brand_pwd = ICPSudo.search([('key', '=', 'admin_pwd')]).value
        dest_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(brand_website))
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(brand_website))
        uid_dst = common.authenticate(db_name, brand_admin, brand_pwd, {})
        self.send_user_increase_mail(db_name,user_to_add)            

        if not tenant.free_trial:

            agreement = request.env['sale.recurring.orders.agreement'].sudo().search([('instance_name', '=', db_name)])
            for order in agreement.order_line:
                total_amount = total_amount + order.order_id.amount_total
                if int(order.order_id.no_of_users) < int(agreement.current_users):
                    user_adding = int(agreement.current_users) - int(order.order_id.no_of_users)
                    user_one = (order.order_id.amount_untaxed / int(order.order_id.no_of_users))
                    total_users = (int(order.order_id.no_of_users) + int(user_adding))
                    total_amount = user_one * + total_users + (order.order_id.amount_tax / total_users)

            expiry_date_tenant_db = tenant.exp_date
            diff_of_today_and_exp_date = expiry_date_tenant_db - datetime.datetime.now().date()

            total_days = 0
            remain_days = diff_of_today_and_exp_date.days

            if agreement.invoice_term_id.name == 'Monthly':
                total_days = 30

                # amount_to_invoice=total_amount/30
                # remaing_days_amount = amount_to_invoice * diff_of_today_and_exp_date.days
                # invoice_amount = remaing_days_amount*int(user_to_add)
            elif agreement.invoice_term_id.name == 'Yearly':
                total_days = 365

                # amount_to_invoice=total_amount/365
                # remaing_days_amount = amount_to_invoice * diff_of_today_and_exp_date.days
                # invoice_amount = remaing_days_amount * int(user_to_add)

            current_users = agreement.current_users
            one_user_price = total_amount / int(current_users)
            one_user_price_for_one_day = one_user_price / total_days
            extra_users_price_for_one_day = one_user_price_for_one_day * int(user_to_add)
            extra_users_price_for_remain_day = extra_users_price_for_one_day * remain_days

            invoice_amount = extra_users_price_for_remain_day

            user_id = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
            sum1 = tenant.no_of_users + int(user_to_add)
            today = time.strftime('%Y-%m-%d')
            journal_id = request.env['account.journal'].sudo().search([('type', '=', 'sale')], limit=1)
            
            from random import randrange
            random_number = randrange(1000)
#             num_add = tenant.random_number()
            num_add = str(random_number)

            number_search = http.request.env['account.move'].sudo().search([])
            random_num = ''
            for num in number_search:
                if agreement.number + ' ' + str(random_num) == num.name + random_num:
                    random_num = num_add

            invoice_vals = {
                'name': agreement.number + ' ' + str(random_num),
                'type': 'out_invoice',
                'invoice_origin': tenant.sale_order_ref.name,
                'ref': 'User Purchase Invoice',
                'date': today,
                # 'address_invoice_id':self.sale_order_ref.partner_invoice_id.id,
                'user_id': request.env.uid,
                'partner_id': tenant.sale_order_ref.partner_id.id,
                # 'account_id':account_id,
                'journal_id': journal_id.id or False,
                # 'sale_order_ids': [(4,self.sale_order_ref.id)],
                'instance_name': str(tenant.name).encode('utf-8'),
                'agreement_id': agreement.id,
                'invoice_type': 'rent',
                'user_count': user_to_add,
                'invoice_line_ids': [],
            }
            # analytic_account = request.env['account.analytic.account'].sudo().create({
            #     'name': 'test account',
            # })
            product_id = agreement.agreement_line.product_id


            invoice_line_vals = {
                'name': agreement.number,
                'price_unit': invoice_amount,
                'price_unit_show': invoice_amount,
                'quantity': 1,
                'product_id': product_id.id,
                'product_uom_id': product_id.uom_id.id,
                'analytic_account_id': False,
                'add_user_line': True,
            }

            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            invoice = http.request.env['account.move'].sudo().create(invoice_vals)

            invoice.sudo().action_post()

            print("\n\n\n\ntotal_amount of agreement", invoice_amount, diff_of_today_and_exp_date)

            sum1 = tenant.no_of_users + int(user_to_add)

        if tenant.free_trial:
            if int(user_to_add) > 0:
                sum1 = tenant.no_of_users + int(user_to_add)
                print(sum1, '================s')
                request.env['user.history'].sudo().create(
                    {'tenant_id': tenant.id, 'pre_users': tenant.no_of_users, 'adding': user_to_add, 'total': sum,
                     'rec_date': datetime.datetime.today()})
                tenant.no_of_users = sum1
                registry = odoo.registry(db_name)
                dest_model.execute_kw(db_name, uid_dst, brand_pwd, 'saas.service', 'write',
                                      [1,
                                       {
                                           'user_count': sum1
                                       }]
                                      )

                # with registry.cursor() as tenant_cr:
                #     tenant_env = odoo.api.Environment(tenant_cr, 1, {})
                #     ret = tenant_env['saas.service'].sudo().browse(1).write({'user_count': sum})

        if sum1:
            return json.dumps(sum1)
        else:
            return {}

    @http.route(['/apps/activate_user_again'], type='http', auth="public", website=True, csrf=False)
    def activate_user_again(self, **post):
        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', post['db'])])
        if tenant:
            registry = odoo.registry(post['db'])
            with registry.cursor() as tenant_cr:
                print(11111111111111111111111111111111111111111111)
                tenant_env = odoo.api.Environment(tenant_cr, 1, {})
                print(22222222222222222222222222222222222222222222222, '=', tenant_env['saas.service'].sudo().browse(1).balance_user_count)
                # print (errrrrrrrrrrrrrrrrrrr)
                service = tenant_env['saas.service'].sudo().browse(1)
                if service.balance_user_count > 0:

                    print(333333333333333333333333333333333333333333333333)
                    sum = service.use_user_count + 1

                    ret = tenant_env['saas.service'].sudo().browse(1).write({'use_user_count': sum})

                    user = tenant_env['res.users'].sudo().search([('active', '=', False), ('login', '=', post['user'])])
                    tenant_cr.execute("update res_users set active='t' where id=%d" % user.id)

                    request.env['user.history'].sudo().create(
                        {'tenant_id': tenant.id, 'pre_users': tenant.no_of_users, 'total': sum, 'rec_date': datetime.datetime.today()})
                    # tenant.no_of_users = sum

                else:
                    print(44444444444444444444444444444444444444444444444444444444444)
                    return json.dumps({'allow': False})

        return json.dumps({'allow': True})

    @http.route(['/apps/remove_users'], type='http', auth="public", website=True, csrf=False)
    def remove_users(self, **post):
        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', post['db'])])
        sum = False
        if tenant:
            print(post, '================s')
            request.env['user.history'].sudo().create(
                {'tenant_id': tenant.id, 'pre_users': tenant.no_of_users, 'total': sum, 'rec_date': datetime.datetime.today()})
            # tenant.no_of_users = sum
            print(tenant.no_of_users, sum)
            registry = odoo.registry(post['db'])
            with registry.cursor() as tenant_cr:
                tenant_env = odoo.api.Environment(tenant_cr, 1, {})
                service = tenant_env['saas.service'].sudo().browse(1)
                sum = service.use_user_count - 1
                service.use_user_count = sum

                user = tenant_env['res.users'].sudo().search([('login', '=', post['user'])])
                tenant_cr.execute("update res_users set active='f' where id=%d" % user.id)
                print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

                ##now create a Invoice of this user

                agreement_order_obj = request.env['sale.recurring.orders.agreement.order'].sudo()
                invoice_line_obj = request.env['account.move.line'].sudo()
                invoice_obj = request.env['account.move'].sudo()
                journal_obj = request.env['account.journal'].sudo()
                today = time.strftime('%Y-%m-%d')
                move_id = None

                ## check agreement is created for this tenant
                agreement_order_id = agreement_order_obj.search([('order_id', '=', tenant.sale_order_ref.id), ('agreement_id.active', '=', True)],
                                                                limit=1)
                if agreement_order_id:
                    res = journal_obj.search([('type', '=', 'sale')], limit=1)
                    journal_id = res and res[0] or False
                    account_id = tenant.sale_order_ref.partner_id.property_account_receivable_id.id
                    invoice_vals = {
                        'name': tenant.sale_order_ref.name,
                        'invoice_origin': tenant.sale_order_ref.name,
                        'comment': 'SaaS Recurring Invoice',
                        'date_invoice': today,
                        'address_invoice_id': tenant.sale_order_ref.partner_invoice_id.id,
                        'user_id': request.session.uid,
                        'partner_id': tenant.sale_order_ref.partner_id.id,
                        'account_id': account_id,
                        'journal_id': journal_id.id,
                        'sale_order_ids': [(4, tenant.sale_order_ref.id)],
                        'instance_name': str(tenant.name).encode('utf-8'),
                        'agreement_id': agreement_order_id.agreement_id.id,
                    }
                    move_id = invoice_obj.create(invoice_vals)
                    print("Created INV ----------", move_id)
                    ## make invoice line from the agreement product line
                    ICPSudo = request.env['ir.config_parameter'].sudo()
                    user_product_id = int(ICPSudo.search([('key', '=', 'buy_product')]).value)

                    for line in agreement_order_id.agreement_id.agreement_line:
                        qty = line.quantity
                        if user_product_id == line.product_id.id:
                            qty = tenant.sale_order_ref.no_of_users
                        invoice_line_vals = {
                            'name': line.product_id.name,
                            'origin': 'SaaS-Kit-' + line.agreement_id.number,
                            'move_id': move_id.id,
                            'uom_id': line.product_id.uom_id.id,
                            'product_id': line.product_id.id,
                            'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
                            'price_unit': line.product_id.lst_price,
                            'discount': line.discount,
                            'quantity': 1,
                            'remove_user_line': True,
                            'account_analytic_id': False,
                        }
                        if line.product_id.taxes_id.id:
                            invoice_line_vals['invoice_line_tax_ids'] = [
                                [6, False, [line.product_id.taxes_id.id]]]  # [(6, 0, [line.product_id.taxes_id.id])],

                        l = invoice_line_obj.create(invoice_line_vals)
                        print("Created INV line ----------", l)

                    # recompute taxes(Update taxes)
                    # if move_id.invoice_line_ids: move_id.compute_taxes()

                # recompute taxes(Update taxes)
                print(move_id, move_id.number, '====================================ss')

                return {}
                if move_id and move_id.invoice_line_ids: move_id.action_post()

                return {}

        return {}


class website_sale(WebsiteSale):

    @http.route(['/shop/shop_cart_custom_update'], type='http', auth="public", website=True)
    def shop_cart_custom_update(self, **post):
        print("shop_cart_custom_update=================", post, request.session)
        print(request.httprequest.environ, 'HOSTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
        domain = ''
        try:
            domain = request.httprequest.environ['HTTP_X_FORWARDED_SERVER']
        except:
            domain = request.httprequest.environ['HTTP_HOST']

        path = request.httprequest.environ['PATH_INFO']
        http = request.httprequest.environ['HTTP_REFERER']
        if 'https' in http:
            http = 'https://'
        else:
            http = 'http://'

        print(domain, path, '\n\n\nUUUUUUUUUUUUUUUUUUUUUUUUUUU')
        if not request.session.uid:
            url = "/web/login?redirect=" + str(http) + "/" + str(domain) + "/" + str(path)

            url = url.replace('//', '/')

            print(url, 'URRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')

            return request.redirect(url)

        order = False

        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()
        if 'product_ids' in request.session:
            ids = request.session['product_ids']

            ids = ids.split(",")
            pro_ids = []
            pro_ids = list(map(int, ids))
            print("pro_ids::::::::::::::::", pro_ids)
            for item in pro_ids:
                print("::::::::::::::::::::::::::::: ", item)

                order = request.website.sale_get_order(force_create=1)._cart_update(
                    product_id=int(item),
                )

        return request.redirect("/shop/address?partner_id=%s" % request.env.user.partner_id.id)

        so_line = request.env['sale.order.line'].sudo().browse(order.get('line_id'))
        render_values = {
            'website_sale_order': so_line.order_id,
            'partner_id': request.env.user.partner_id,
            'mode': ('edit', 'billing'),
            'checkout': so_line.order_id.partner_id,
            'country': None,  # country,
            'countries': request.env['res.country'].search([]),  # country.get_website_sale_countries(mode='edit'),
            "states": None,  # country.get_website_sale_states(mode='edit'),
            'error': {},
            'callback': None,
        }
        print("Partner ==========", so_line.order_id.partner_id)
        print("\n\nreturning address from shop_cart_custom_update", render_values)
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/checkout2topup'], type='http', auth="public", website=True)
    def checkout2topup(self, **post):
        if 'db_id' in post and post['db_id']:
            ICPSudo = request.env['ir.config_parameter'].sudo()
            trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)
            today = time.strftime('%Y-%m-%d')
            tenant = request.env['tenant.database.list'].sudo().search([('id', '=', int(post.get('db_id')))])
            exp_date1 = datetime.datetime.strptime(str(tenant.exp_date), '%Y-%m-%d').date()
            today = datetime.datetime.strptime(str(today), '%Y-%m-%d').date()
            # if trial_days > 0 and exp_date1 >= today:
            #     request.session['show_payment_acquire'] = False
            # else:
            #     request.session['show_payment_acquire'] = True

        sale_order = False
        tenant = request.env['tenant.database.list'].sudo().search([('id', '=', int(post.get('db_id')))])
        pricelist_id = request.session.get('website_sale_current_pl') or request.env['website'].get_current_pricelist().id
        partner = request.env.user.partner_id
        pricelist = request.env['product.pricelist'].browse(pricelist_id).sudo()
        so_data = request.env['website'].sudo().browse(1)._prepare_sale_order_values(partner, pricelist)
        so_data['instance_name'] = tenant.name

        term = tenant.sale_order_ref.invoice_term_id

        so_data['invoice_term_id'] = term.id
        so_data['no_of_users'] = tenant.no_of_users
        so_data['is_top_up'] = True

        if 'sale_order_id' in request.session and request.session['sale_order_id']:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', int(request.session['sale_order_id']))])
            sale_order.write(so_data)
            print(sale_order, '____________________1')
        else:
            sale_order = request.env['sale.order'].sudo().create(so_data)
            request.session['sale_order_id'] = sale_order.id
            print(sale_order, '____________________2')

        if post.get('ids'):
            if 'product_ids' in request.session:
                request.session['product_ids'] = ''

            request.session['product_ids'] = post.get('ids')
            id_list = post.get('ids').split(',')
            id_list = list(map(int, id_list))
            for id in id_list:
                print(sale_order, '____________________3')
                sale_order._cart_update(product_id=id, set_qty=1)

    @http.route(['/shop/checkout2buy'], type='http', auth="public", website=True)
    def checkout2buy(self, **post):

        ICPSudo = request.env['ir.config_parameter'].sudo()
        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)
        # if 'new_instance' in post and post['new_instance'] in [True, 'True', 'true'] and trial_days > 0:
        #     request.session['show_payment_acquire'] = False
        # else:
        #     request.session['show_payment_acquire'] = True

        sale_order = False
        pricelist_id = request.session.get('website_sale_current_pl') or request.env['website'].get_current_pricelist().id
        partner = request.env.user.partner_id
        pricelist = request.env['product.pricelist'].browse(pricelist_id).sudo()
        so_data = request.env['website'].browse(1)._prepare_sale_order_values(partner, pricelist)
        so_data['instance_name'] = post.get('dbname')
        print("Posttttttttttttttttt", post)
        if 'term' in post:
            term = request.env['recurring.term'].sudo().search([('type', '=', post.get('term'))])
            so_data['invoice_term_id'] = term.id
        so_data['no_of_users'] = post.get('num')
        so_data['is_top_up'] = False
        # print("\n\n\n\n\n\n  s-DATA ::::: ",so_data,"\n\n\n")
        if 'sale_order_id' in request.session and request.session['sale_order_id']:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', int(request.session['sale_order_id']))])
            sale_order.write(so_data)
            print(sale_order, '____________________1')
        else:
            sale_order = request.env['sale.order'].sudo().create(so_data)
            request.session['sale_order_id'] = sale_order.id
            print(sale_order, '____________________2')
        # print("\n\n#######post#########\n\n", post, "\n\n")

        # Delete/Unlink exist product lines
        exist_ids = []
        for item in sale_order.order_line:
            exist_ids.append((3, item.id, False))
        sale_order.order_line = exist_ids

        if post.get('ids'):
            if 'product_ids' in request.session:
                request.session['product_ids'] = ''

            request.session['product_ids'] = post.get('ids')
            id_list = post.get('ids').split(',')
            id_list = list(map(int, id_list))
            for id in id_list:
                print(sale_order, '____________________3')
                sale_order._cart_update(product_id=id, set_qty=1)

        exist = False
        for sale in request.env['sale.order'].sudo().search([('state', '!=', 'cancel'),('state', '!=', 'draft'), ('id', '!=', sale_order.id)]):
            if sale.instance_name and sale.instance_name == post['dbname']:
                exist = True
                break

        return json.dumps({'exist': exist})

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        print("\n\n\nKw--in addresssssssss-----------------", kw, Partner, Partner.email)
        order = request.website.sale_get_order()
        print(1111111111111111111111111111)
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        print(22222222222222222222222222222)
        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}
        print(3333333333333333333333333333333333)
        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        print("Partnersssssssssssssssssssss", order.partner_id.id, request.website.user_id.sudo().partner_id.id)
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].sudo().search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            print("partner_id-----------------", partner_id)
            if partner_id > 0:
                print("11111111111111111111", partner_id, order.partner_id.id)
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        print("Forbidden================")
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
                    print("values================", values)
            elif partner_id == -1:
                print("22222222222222222222222")
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                print("3333333333333")

                return request.redirect('/shop/confirm_order')
                # return request.redirect('/shop/payment/confirmation/%s' % order.id)
        print("Again kwwwwwwwwwwwwwwwww", kw)
        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            print("postttttttttttttttttttttttttttttt", post)
            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                order.customer_name = post['name'] if 'name' in post else ''
                order.customer_email = post['email'] if 'email' in post else ''

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    print("\n\nReturning from address to confirm_order======================", errors)

                    request.env.cr.commit()
                    # return request.redirect('/shop/confirm_order
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')
                    # return request.redirect(kw.get('callback') or '/shop/payment/confirmation/%s' % order.id)

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id

        print("Adreessss page values\=\\=====================", values, country.exists())
        if not order.customer_email:
            print("\n\n\n\nSetting customer_email from myyyy codeeee\n\n\n")
            if order.partner_id.email:
                order.customer_email = order.partner_id.email
        print("order============", order)
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        print("\n\nreturning address pageeeeeeeeeeeeeee", render_values, '\nvalues=========', values)
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        order = request.website.sale_get_order()
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n IN OUR ORDER :::::: ", order, post, "\n\n\n\n\n\n\n\n")
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        print("\n\n render_values:::::: ", render_values, request.session, "\n\n")
        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')
        # if 'sale_order_id' in request.session:
        #     request.session['sale_order_id']=''

        show = False
        if 'showing' in request.session:
            print("request.session['showing']:::::::::::::::::::::::@@@@@@@@@@@@@@", request.session['showing'])
            if request.session['showing'] == 2:
                render_values['showing'] = 2

        ICPSudo = request.env['ir.config_parameter'].sudo()
        if 'show_payment_acquire' in request.session and request.session['show_payment_acquire'] is True:
            show = True

        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)
        render_values['show_payment_acquire'] = show
        render_values['free_days'] = trial_days

        ## IF SHOW PAYMENTS DETAILS IS FALSE THE CARRY ONLY ONE ACQUIRER "WIRE TRANSFER"
        if show is False:
            acq = []
            for item in render_values['acquirers']:
                print(item.name, 'ITEMNAMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
                if 'Wire' in item.name or item.provider == 'transfer':
                    acq.append(item)
            render_values['acquirers'] = acq
            render_values['hide_acquirer_div'] = True
        else:
            render_values['hide_acquirer_div'] = False
        if show is True:
            acq = []
            for item in render_values['acquirers']:
                payment_mth = ICPSudo.search([('key', '=', 'payment_acquire')]).value
                print("payment_mth::::::::::::::::::", payment_mth)
                acquire = request.env['payment.acquirer'].search([('id', '=', int(payment_mth))])
                print("acquire::::::::::::", acquire.id)
                print("item::::::::::::", item.id)
                if acquire.id == item.id:
                    pass
                else:
                    acq.append(item)
            render_values['acquirers'] = acq

        print(render_values, "REN VALUESSSSSSSSSSSSSSSSSSSSSSSSS")

        return request.render("website_sale.payment", render_values)

    @http.route(['/shop/clear_cart'], type='json', auth="public", website=True)
    def clear_cart(self):
        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.
   
        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        # Ensure a payment acquirer is selected
        print("In payment_transaction==================", kwargs, request.session)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()
            if not order:
                order = request.env['sale.order'].sudo().search([('id', '=', request.session['sale_order_id'])])
            print("\n\n\n\n\n\n\n ORDER IS:::::::::", order)
        # Ensure there is something to proceed
        ICPSudo = request.env['ir.config_parameter'].sudo()
        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)

        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', order.instance_name)])
        payment_id = ICPSudo.search([('key', '=', 'payment_acquire')]).value

        print("tenant::::::::::::::::::::;", tenant, request.session['show_payment_acquire'])
        if tenant:
            today = time.strftime('%Y-%m-%d')
            today = datetime.datetime.strptime(str(today), '%Y-%m-%d').date()
            exp_date1 = datetime.datetime.strptime(str(tenant.exp_date), '%Y-%m-%d').date()
            if trial_days > 0 and exp_date1 >= today and request.session['show_payment_acquire'] == False:
                if int(acquirer_id) != int(payment_id):
                    acquirer_id = int(payment_id)

                # order.action_confirm1()


        else:
            if trial_days > 0 and request.session['show_payment_acquire'] == False:
                if int(acquirer_id) != int(payment_id):
                    acquirer_id = int(payment_id)
                # order.action_confirm1()

        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)
        print("vals--transactionnnnnn--------------", vals, order)
        transaction = order._create_payment_transaction(vals)
        print("transaction===================", transaction)
        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
            print("ther111111111111111111111111111111111111")
        PaymentProcessing.add_payment_transaction(transaction)
        print("!!!!!!!!!!!!!!!")
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)

    # @http.route(['/shop/payment/transaction/',
    #     '/shop/payment/transaction/<int:so_id>',
    #     '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    # def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
    #     """ Json method that creates a payment.transaction, used to create a
    #     transaction when the user clicks on 'pay now' button. After having
    #     created the transaction, the event continues and the user is redirected
    #     to the acquirer website.
    #
    #     :param int acquirer_id: id of a payment.acquirer record. If not set the
    #                             user is redirected to the checkout page
    #     """
    #
    #     tx_type = 'form'
    #     if save_token:
    #         tx_type = 'form_save'
    #
    #     # In case the route is called directly from the JS (as done in Stripe payment method)
    #     if so_id and access_token:
    #         order = request.env['sale.order'].sudo().search([('id', '=', so_id), ('access_token', '=', access_token)])
    #     elif so_id:
    #         order = request.env['sale.order'].search([('id', '=', so_id)])
    #     else:
    #         order = request.website.sale_get_order()
    #         if not order:
    #             order = request.env['sale.order'].search([('id','=',request.session['sale_order_id'])])
    #         print("\n\n\n\n\n\n\n ORDER IS:::::::::",order)
    #     if not order or not order.order_line or acquirer_id is None:
    #         return False
    #
    #     assert order.partner_id.id != request.website.partner_id.id
    #
    #     # find or create transaction
    #     # tx = request.website.sale_get_transaction() or request.env['payment.transaction'].sudo()
    #     tx = request.env['payment.transaction'].sudo()
    #     acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
    #     payment_token = request.env['payment.token'].sudo().browse(int(token)) if token else None
    #     tx = tx._check_or_create_sale_tx(order, acquirer, payment_token=payment_token, tx_type=tx_type)
    #     request.session['sale_transaction_id'] = tx.id
    #     return tx.render_sale_button(order, '/shop/payment/validate')

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        print("payment_validate1:::::::::::::::::::::::::::::::::::::::::::::")
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentProcessing.remove_payment_transaction(tx)
        return request.redirect('/shop/confirmation')

    @http.route(['/shop/order_confirm'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation_order(self, **post):
        print("payment_confirmation243333333333:::::::::::::::::::::::::::::::::::::::::::")
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        ICPSudo = request.env['ir.config_parameter'].sudo()
        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)

        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            print("ffffffffffffffffffffffffffffffffffff$$$$$$$$$$$$$$")
            if 'show_payment_acquire' in request.session:
                order.action_confirm1()
        else:
            raise UserError('no sale order')

        if 'show_payment_acquire' in request.session:
            del request.session['show_payment_acquire']
        if 'showing' in request.session:
            del request.session['showing']
        if 'select_payment_option' in request.session:
            del request.session['select_payment_option']
        return request.render("saas_product.confirmation1", {'order': order})

    @http.route(['/check/payment/method'], type='json', auth="public", website=True, sitemap=False)
    def check_payment_method(self, **post):
        ICPSudo = request.env['ir.config_parameter'].sudo()
        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)
        order = request.website.sale_get_order()
        tenant_topup = True
        if not order:
            if 'sale_order_id' in request.session:
                order = request.env['sale.order'].sudo().search([('id', '=', request.session['sale_order_id'])])

        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', order.instance_name)])

        if tenant:
            today = time.strftime('%Y-%m-%d')
            today = datetime.datetime.strptime(str(today), '%Y-%m-%d').date()
            exp_date1 = datetime.datetime.strptime(str(tenant.exp_date), '%Y-%m-%d').date()

            if exp_date1 >= today:
                tenant_topup = True
            else:
                tenant_topup = False

        if post.get('payment_value') == 'False':
            request.session['show_payment_acquire'] = False
            if tenant_topup == True:
                if trial_days > 0:
                    request.session['showing'] = 2
            else:
                if tenant_topup == False:
                    request.session['showing'] = False
            request.session['select_payment_option'] = post.get('payment_value')
            return {
                'state': int(trial_days),
                'message': False,
                'tenant_topup': tenant_topup
            }
        else:
            request.session['show_payment_acquire'] = True
            request.session['select_payment_option'] = post.get('payment_value')
            return {
                'message': True, }

    @http.route(['/get_applicant_details'], type='http', auth="public", website=True, sitemap=False)
    def check_get_value(self, **post):
        ICPSudo = request.env['ir.config_parameter'].sudo()
        trial_days = int(ICPSudo.search([('key', '=', 'free_trial_days')]).value or 0)
        order = request.website.sale_get_order()
        tenant_topup = True
        if not order:
            order = request.env['sale.order'].sudo().search([('id', '=', request.session['sale_order_id'])])
        tenant = request.env['tenant.database.list'].sudo().search([('name', '=', order.instance_name)])

        if tenant:
            today = time.strftime('%Y-%m-%d')
            today = datetime.datetime.strptime(str(today), '%Y-%m-%d').date()
            exp_date1 = datetime.datetime.strptime(str(tenant.exp_date), '%Y-%m-%d').date()
            if exp_date1 >= today:
                tenant_topup = True
            else:
                tenant_topup = False

        if trial_days <= 0 or tenant_topup == False:
            if 'select_payment_option' in request.session:
                if 'show_payment_acquire' in request.session:
                    if request.session['show_payment_acquire'] == False:
                        request.session['select_payment_option'] = 'no_option'
            # print("::::::::::::::",request.session['showing'])
            # if 'showing' in request.session:
            #     request.session['showing']= False




        result = {}
        if 'select_payment_option' in request.session:
            result = {'select_payment_option': request.session['select_payment_option']}
        else:
            result = {'select_payment_option': 'no_option'}

        return json.dumps(result)

        # return request.redirect("/shop/payment")
    
    

