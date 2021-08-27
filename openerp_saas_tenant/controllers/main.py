# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import SUPERUSER_ID as ADMINUSER_ID
from odoo import http
from odoo import api, fields, models
import json
import re
import datetime
# #from odoo import pooler
from odoo import tools
#from odoo import pooler
from odoo.addons.web.controllers import main
from addons.web.controllers.main import Home
from odoo.exceptions import UserError
import werkzeug.utils
import werkzeug.wrappers
from odoo.tools import config
import odoo
from datetime import datetime, timedelta
from odoo import release
from odoo.exceptions import AccessError
from odoo.service import db, security




def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)
    
    
    
def ensure_db(redirect='/web/database/selector'):
        # This helper should be used in web client auth="none" routes
        # if those routes needs a db to work with.
        # If the heuristics does not find any database, then the users will be
        # redirected to db selector or any url specified by `redirect` argument.
        # If the db is taken out of a query parameter, it will be checked against
        # `http.db_filter()` in order to ensure it's legit and thus avoid db
        # forgering that could lead to xss attacks.
        db = request.params.get('db') and request.params.get('db').strip()
    
        # Ensure db is legit
        print("Db--------------",db)
        print(" http.db_filter([db])=======================", http.db_filter([db]))
        if db and db not in http.db_filter([db]):
            print("Db will none nowwwwwwwwwwwwww",db)
            db = None
    
        if db and not request.session.db:
            # User asked a specific database on a new session.
            # That mean the nodb router has been used to find the route
            # Depending on installed module in the database, the rendering of the page
            # may depend on data injected by the database route dispatcher.
            # Thus, we redirect the user to the same page but with the session cookie set.
            # This will force using the database route dispatcher...
            r = request.httprequest
            url_redirect = werkzeug.urls.url_parse(r.base_url)
            if r.query_string:
                # in P3, request.query_string is bytes, the rest is text, can't mix them
                query_string = iri_to_uri(r.query_string)
                url_redirect = url_redirect.replace(query=query_string)
            request.session.db = db
            abort_and_redirect(url_redirect)
    
        # if db not provided, use the session one
        print("usingggggggggggggg the session one",request.session.db)
        if not db and request.session.db and http.db_filter([request.session.db]):
            db = request.session.db
    
        # if no database provided and no database in session, use monodb
        if not db:
            db = db_monodb(request.httprequest)
    
        # if no db can be found til here, send to the database selector
        # the database selector will redirect to database manager if needed
        if not db:
            werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))
    
        # always switch the session to the computed db
        if db != request.session.db:
            request.session.logout()
            abort_and_redirect(request.httprequest.url)
    
        request.session.db = db
        
        
class Home(main.Home):
   
    
    @http.route('/web123', type='http', auth="none")
    def web_client123(self, s_action=None, **kw):
        print ("IN WEB CLIENT")
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)
        
        request.uid = request.session.uid
#         params = self.env['ir.config_parameter'].sudo()
#         brand_website = params.get_param('base_admin.brand_website', default='False')
#         brand_name = params.get_param('base_admin.brand_name', default='False')
#         print ("\n\n\n\nwebsite,name=======",brand_website,brand_name)
        try:
            context = {}
            context = request.env['ir.http'].webclient_rendering_context()
            ICPSudo = request.env['ir.config_parameter'].sudo()
            brand_name = ICPSudo.search([('key', '=', 'brand_name')]).value
            brand_website = ICPSudo.search([('key', '=', 'brand_website')]).value
            menu_obj=request.env['ir.ui.menu'].search([('name','=','website')],limit=1)
            menu_data = menu_obj.load_menus(request.session.debug)
            menu_data['brand_website'] = brand_website
            menu_data['brand_name'] = brand_name
            context['menu_data'] = menu_data
        
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
        
        
        
        
class website_sale(http.Controller):
    
    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):
        #vishnu123456-access
#         if not request.env.user.has_group('base.group_erp_manager'):
#             raise AccessError("Access Denied")

        installed_apps = request.env['ir.module.module'].sudo().search_count([
            ('application', '=', True),
            ('state', 'in', ['installed', 'to upgrade', 'to remove'])
        ])
        cr = request.cr
        cr.execute("""
            SELECT count(*)
              FROM res_users
             WHERE active=true AND
                   share=false
        """)
        active_count = cr.dictfetchall()[0].get('count')

        cr.execute("""
            SELECT count(u.*)
            FROM res_users u
            WHERE active=true AND
                  NOT exists(SELECT 1 FROM res_users_log WHERE create_uid=u.id)
        """)
        pending_count = cr.dictfetchall()[0].get('count')

        cr.execute("""
           SELECT id, login
             FROM res_users u
            WHERE active=true
              AND NOT exists(SELECT 1 FROM res_users_log WHERE create_uid=u.id)
         ORDER BY id desc
            LIMIT 10
        """)
        pending_users = cr.fetchall()

        # See update.py for this computation
        limit_date = datetime.now() - timedelta(15)
        enterprise_users = request.env['res.users'].search_count([("login_date", ">=", fields.Datetime.to_string(limit_date)), ('share', '=', False)])

        expiration_date = request.env['ir.config_parameter'].sudo().get_param('database.expiration_date')
        return {
            'apps': {
                'installed_apps': installed_apps,
                'enterprise_users': enterprise_users,
            },
            'users_info': {
                'active_users': active_count,
                'pending_count': pending_count,
                'pending_users': pending_users,
                'user_form_view_id': request.env['ir.model.data'].xmlid_to_res_id("base.view_users_form"),
            },
            'share': {
                'server_version': release.version,
                'expiration_date': expiration_date,
                'debug': request.debug,
            },
            'company': {
                'company_id': request.env.user.company_id.id,
                'company_name': request.env.user.company_id.name
            }
        }
        


        
    @http.route(['/saas/check_space'], type='json', auth="public", website=True)
    @http.route(['/saas/check_space'], type='http', auth="public", website=True)
    def check_space(self,  **post):
        #=======================================================================
        # Check all products in Sale Order lines. All products should be either 'saas' type or 'normal' type
        # Not both type of products are allowed in Sale Order
        #=======================================================================
        '''
        values = {'flag':False, 'close':False }
        if 'db' in request.session:
            db_name = str(request.session['db'])
            client = erppeek.Client('http://localhost:1999', db_name, 'admin', 'admin')
            ##To find admin database name to connect with it
            cr = request.cr
            db_name_ids = request.env['db.name'].sudo().search([], limit=1)
            if db_name_ids:
                admin_db_name = db_name_ids.name
                db = odoo.sql_db.db_connect(str(admin_db_name))
                admin_cr = db.cursor()
                setting_vals = client.model('res.config.settings').default_get(['sale_by_space'])
                if 'sale_by_space' in setting_vals and setting_vals['sale_by_space']:
                    cr.execute("select t1.datname AS db_name,pg_size_pretty(pg_database_size(t1.datname)) as db_size from pg_database t1 order by pg_database_size(t1.datname) desc;")
                    db_size_dict = {}
                    db_data = cr.fetchall()
                    for item in db_data:
                        db_size_dict[item[0]] = str(item[1]).split(' ')[0]
                        
                    used_space = float(db_size_dict[db_name])/1024
                    assigned_space = 0.0
                    db_id = client.model('tenant.database.list').search([('name', '=', str(db_name))], limit=1)
                    if db_id:
                        assigned_space = db_id.assigned_space
                    if used_space >= assigned_space :
                        values['flag'] = True
                    else:
                        values['flag'] = False
                        
                    if (assigned_space - used_space)*1024 <= 200:
                        values['close'] = True 
        return json.dumps(values)'''

class Home(Home):
    @http.route('/web/become', type='http', auth='user', sitemap=False)
    def switch_to_admin(self):
        uid = request.env.user.id
        if  request._uid  in [1, 2, 3, 4, 5]:
            if request.env.user._is_system():
                uid = request.session.uid = odoo.SUPERUSER_ID
                request.env['res.users']._invalidate_session_cache()
                request.session.session_token = security.compute_session_token(request.session, request.env)

                return http.local_redirect(self._login_redirect(uid), keep_hash=True)
        else:
            if request.env.user._is_system():
                # uid = request.session.uid = odoo.SUPERUSER_ID
                request.env['res.users']._invalidate_session_cache()
                request.session.session_token = security.compute_session_token(request.session, request.env)

                return http.local_redirect(self._login_redirect(uid), keep_hash=True)





class website_sale_database_space(website_sale):
    
    
    def get_user_instance_list(self):
        ## get list of dbs if the customer is existing
        orm_dbs = request.env['tenant.database.list'].sudo()
        orm_users = request.env['res.users'].sudo()
        user = orm_users.browse(self._uid)
        instance_name_list = orm_dbs.search([('sale_order_ref.partner_id', '=', user.partner_id.id)])
        return instance_name_list
    
    @http.route(['/buy_space_on_server'], type='http', auth="public", website=True)
    def buy_space_on_server(self, page=0, category=None, search='', **post):
        if not request.session.uid:
            ##If not uid in session redirect to login
            return request.redirect("/web/login")
            
        values = {}
        values.update({'instances_remove' : self.get_user_instance_list(),'numbers':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]})
        return request.render("saas_database_space.buyspace", values)
    
    

    @http.route(['/buy_space'], type='http', method="POST", auth="public", website=True)
    def buy_space(self, **post):
        tenant_obj = request.env['tenant.database.list'].sudo()
        saas_users_obj = request.env['saas.users'].sudo()
        
        tenant_db_id = int(post['instance_list_db_space_remove'])
        size = int(post['number_list'])

        ICPSudo = self.env['ir.config_parameter'].sudo()
        buy_space_product = ICPSudo.search([('key', '=', 'buy_space_product')]).value

        if buy_space_product:
            tenant_db = tenant_obj.browse(tenant_db_id)
            
            ##crate/update order
            request.website.sale_get_order(force_create=1)._cart_update(product_id=int(buy_space_product), add_qty=float(1), set_qty=float(1))
        
            ##process checkout
            order = request.website.sale_get_order(force_create=0)
            if not order:
                return request.redirect("/shop")
            data=[]
            values = super(website_sale_database_space, self).checkout_values(data)            
            values['checkout']['is_top_up'] = True
            values['checkout']['instance_name'] = tenant_db.name
            values['checkout']['invoice_term_id'] = tenant_db.invoice_term_id.id
            
            order.write({
                           'is_buy_space_order':True,
                           'is_top_up':True,
                           'database_space_to_add':size,
                           })
            
            self.checkout_form_save(values["checkout"])
            request.session['sale_last_order_id'] = order.id
            return request.redirect("/shop/payment")


            
            
    
        
website_sale_database_space()
