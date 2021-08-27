from odoo.api import Environment
from odoo.http import request
from odoo import http
from odoo import api, fields, models
import json
import odoo
from odoo.tools import config

ADMINUSER_ID = 2

from odoo.addons.web.controllers.main import Database

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

from odoo.addons.web.controllers.main import Home
from addons.web.controllers import main
import re

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.exceptions import AccessError, UserError, AccessDenied


class home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None,csrf=False,**kw):

        # print("kkkkkkkkkkk",kw)


        res = super(home, self).web_login(redirect, **kw)

        expire = False
        try:
            expire = request.env['db.expire'].search([], limit=1)
        except Exception as e:
            print("Error")

        print("bbbbbbbbbb1111",expire)
        if expire and expire.db_expire == True:
            response = request.render('openerp_saas_tenant.login_locked', {})
            return response
        else:
            return res


class Database_Manager(http.Controller):

    @http.route('/web/check_manage_db', auth='public', website=True, csrf=False)
    def check_manage_db(self, **kw):
        request.session.logout(keep_db=True)
        try:
            uid = request.session.authenticate(config['db_name'] or 'saasmaster', kw['user_id'], kw['user_pwd'])
            if uid:
                user = request.env['res.users'].sudo().browse(uid)
                if user.has_group("saas_base.manage_page"):
                    request.session['allow'] = True
                    return http.local_redirect('/web/database/manager')
                else:
                    response = request.render('db_filter.manage_select_db',
                                              {"error": "You don't have access to this page"})
                    return response
            else:
                response = request.render('db_filter.manage_select_db', {"error": "Username or Password is wrong"})
                return response
        except Exception as e:
            response = request.render('db_filter.manage_select_db', {"error": str(e)})
            return response

    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):

        if 'allow' in request.session and request.session['allow'] is True:
            request._cr = None
            request.session['allow'] = False
            del request.session['allow']
            return Database._render_template(self, manage=False)
        else:
            response = request.render('db_filter.manage_select_db', {'error': ""})
            return response

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        if 'allow' in request.session and request.session['allow'] is True:
            request._cr = None
            request.session['allow'] = False
            del request.session['allow']
            return Database._render_template(self)
        else:
            response = request.render('db_filter.manage_select_db', {'error': ""})
            return response


def db_filter(dbs, httprequest=None):
    httprequest = httprequest or request.httprequest
    main_database = 'saasmaster'
    databases = odoo.service.db.list_dbs(True)
    dbs = databases
    test_db = False

    try:
        from contextlib import closing
        chosen_template = odoo.tools.config['db_template']
        templates_list = tuple(set(['postgres', chosen_template]))
        db = odoo.sql_db.db_connect('postgres')
        with closing(db.cursor()) as cr:
            try:
                cr.execute(
                    "select datname from pg_database where datdba=(select usesysid from pg_user where usename=current_user) and not datistemplate and datallowconn and datname not in %s order by datname",
                    (templates_list,))
                dbs = [odoo.tools.ustr(name) for (name,) in cr.fetchall()]
            except Exception:
                import traceback
                print(traceback.format_exc())
    except Exception as e:
        print(e)

    # print("test_db = False:::::::::::::",test_db)
    if httprequest.environ.get('HTTP_X_FORWARDED_SERVER', False):
        h = httprequest.environ.get('HTTP_X_FORWARDED_HOST', '')
        # print("host::::::::::::::::::::;;:1",h)

        # registry = odoo.registry(main_database)
        # with registry.cursor() as cr:
        #     env = Environment(cr, ADMINUSER_ID, {})
        #     try:
        #         tenant_db_list = env['tenant.database.list'].sudo().sudo().search([])
        #         for masking_url in tenant_db_list:
        #             # print("masking_url:::::::::::", masking_url)
        #             for client_domain_name in masking_url.domain_masking_fields:
        #                 if client_domain_name.client_domain == h:
        #                     test_db = True
        #                     break;
        #     except Exception as e:
        #         test_db = False

        # print("host::::::::::::::::::::;;:2", test_db)
        if h:
            h = httprequest.environ.get('HTTP_X_FORWARDED_HOST').split(".")[0]

            d, xyz, r = h.partition('.')
            # print(d, '\n Database after partitionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn\n',main_database)
            if d == main_database:
                d = main_database
            if d in dbs and test_db == False:
                # print("Foundin DB listtttttttttttttttt", d)
                return [d]
                r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)


            elif h :
                # print("Foundin:::::::::::::")
                registry = odoo.registry(main_database)
                with registry.cursor() as cr:
                    env = Environment(cr, ADMINUSER_ID, {})

                    try:
                        db_list = env['tenant.database.list'].sudo().sudo().search([])
                        # print("host:::::::::::::::::::::::::::::::::::::::9")
                        for name in db_list:
                            m = httprequest.environ.get('HTTP_X_FORWARDED_HOST')
                            # print("host:::::::::::::::::::::::::::::::::::::::10",name)

                            try:
                                if name.domain_masking_fields:
                                    # print("host:::::::::::::::::::::::::::::::::::::::11", name.domain_masking_fields)
                                    for nnn in name.domain_masking_fields:
                                        # print("host:::::::::::::::::::::::::::::::::::::::3",nnn)

                                        if m == nnn.client_domain:
                                            h = nnn.tenant_name

                                            h = h.split(".")[0]

                                            d, xyz, r = h.partition('.')

                                            if d in dbs:
                                                # print("Foundin DB listtttttttttttttttt", d)
                                                return [d]
                                                r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)

                                        else:
                                            d=main_database
                                            # return [d]
                                            r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)

                                else:
                                    d = main_database
                                    # print("host:::::::::::::::::::::::::::::::::::::::8",h)
                                    return [d]
                                    r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)




                            except Exception as e:
                                # print("host:::::::::::::::::::::::::::::::::::::::16")
                                return [main_database]

                        else:
                            # print("host:::::::::::::::::::::::::::::::::::::::7")
                            d = main_database
                            return [d]
                            r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)

                    except Exception as e:
                        # print("host:::::::::::::::::::::::::::::::::::::::4")
                        return [main_database]

            else:
                # print("host:::::::::::::::::::::::::::::::::::::::6")
                return [main_database]

            if d=='saasmaster':
                # print("host:::::::::::::::::::::::::::::::::::::::15")
                return [d]
                r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)


            if d == 'www':
                d = r.partition('.')[0]
                r = odoo.tools.config['dbfilter'].replace('%h', h).replace('%d', d)
                filter_dbs = [d]
                dbs = [i for i in dbs if i in filter_dbs]
            if not dbs:
                dbs = [main_database]
        if main_database in dbs:
            # print("host:::::::::::::::::::::::::::::::::::::::12")
            httprequest.environ['HTTP_X_FORWARDED_HOST'] = httprequest.environ['HTTP_X_FORWARDED_SERVER']

    # print(dbs, '\nlast databasesssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
    return dbs


http.db_filter = db_filter
