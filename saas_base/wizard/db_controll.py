# -*- coding: utf-8 -*-
from odoo import api, fields, models
import psycopg2
from odoo import exceptions
from odoo import SUPERUSER_ID, api
from odoo import sql_db, _
import odoo
import datetime
from odoo.tools.translate import _
from odoo.tools import config
from odoo.service import db
from datetime import datetime
from contextlib import closing
import traceback


class db_controll_wizard(models.TransientModel):
    """ Manually Deactivating the database"""
    _name = 'deactive_db.wizard'
    _description = 'DeActivate Database'

    db_name = fields.Many2one('tenant.database.list', 'Select Database', required=True)
    reason = fields.Text('Reason')

    #     def cancel(self,cr,uid,ids,conText=None):
    #         return { 'type':'ir.actions.act_window_close' }
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    #     def deactivate_db(self, cr, uid, ids, data, conText=None):
    #         config = odoo.tools.config
    #         tenant_db_list_obj = self.pool.get('tenant.database.list')
    #         tenant_db = self.browse(cr,uid,ids)[0].db_name
    #         exp_date = tenant_db.exp_date
    #         print exp_date,exp_date,'============='
    #         db_name = self.browse(cr,uid,ids)[0].db_name.name
    #         user_id = uid
    #         reason = self.browse(cr,uid,ids)[0].reason
    #         try : cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s"%{'db':db_name ,'role':'expired_db_owner'})
    #         except Exception as e:
    #             raise osv.except_osv(_('Error!'), _(e))
    #
    #         stage_ids = self.pool.get('tenant.database.stage').search(cr, uid, [('is_deactivated', '=', True)])
    #         tenant_db_list_obj.write(cr,uid,[tenant_db.id],{'expired':True,
    #                                                         'user_id':user_id,
    #                                                         'reason':reason,
    #                                                         'exp_date':exp_date,
    #                                                         'deactivated_date':datetime.now().strftime('%Y-%m-%d'),
    #                                                         'stage_id':stage_ids[0] if stage_ids else False})
    #         cr.commit()
    #         return{
    #           'view_type': 'kanban',
    #           'view_mode': 'kanban',
    #           'res_model': 'tenant.database.list',
    #           'conText': conText,
    #           'type': 'ir.actions.act_window',
    #           }
    def deactivate_db(self):
        config = odoo.tools.config
        tenant_db_list_obj = self.env['tenant.database.list']
        tenant_db = self.db_name
        exp_date = tenant_db.exp_date
        print(exp_date, exp_date, '=============')
        db_name = self.db_name.name
        user_id = self._uid
        reason = self.reason
        cr = self._cr
        try:
            cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': db_name, 'role': 'expired_db_owner'})
        except Exception as e:
            raise exceptions.except_orm(_("Error!"), _(e))

        stage_ids = self.env['tenant.database.stage'].search([('is_deactivated', '=', True)])
        tenant_db.write({'expired': True,
                         'user_id': user_id,
                         'reason': reason,
                         'exp_date': exp_date,
                         'deactivated_date': datetime.now().strftime('%Y-%m-%d'),
                         'stage_id': stage_ids[0].id if stage_ids else False})
        cr.commit()
        return {
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'tenant.database.list',
            'context': self._context,
            'type': 'ir.actions.act_window',
        }

    #     def activate_db(self, cr, uid, ids, data, conText=None):
    #         config = odoo.tools.config
    #         tenant_db_list_obj = self.pool.get('tenant.database.list')
    #         tenant_db = self.browse(cr,uid,ids)[0].db_name
    #         db_name = self.browse(cr,uid,ids)[0].db_name.name
    #         expiry_date_str = str(self.browse(cr,uid,ids)[0].db_name.exp_date).split("-")
    #         exp_date = datetime(int(expiry_date_str[0]),int(expiry_date_str[1]),int(expiry_date_str[2]))
    #         today = datetime.today()
    #         if exp_date > today:
    #             try : cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s"%{'db':db_name ,'role':config['db_user']})
    #             except Exception as e:
    #                 raise osv.except_osv(_('Error!'), _(e))
    #
    #             stage_ids = self.pool.get('tenant.database.stage').search(cr, uid, [('is_active', '=', True)])
    #             tenant_db_list_obj.write(cr,uid,[tenant_db.id],{'expired':False,
    #                                                             'stage_id':stage_ids[0] if stage_ids else False})
    #             cr.commit()
    #         else :
    #             raise osv.except_osv(_('Warning!'), _('Sorry, you can not activate the Database...!'))
    #         return{
    #           'view_type': 'kanban',
    #           'view_mode': 'kanban',
    #           'res_model': 'tenant.database.list',
    #           'conText': conText,
    #           'type': 'ir.actions.act_window',
    #           }
    def activate_db(self):
        saas_db_name = self.env.cr.dbname
        db = sql_db.db_connect(saas_db_name)
        with closing(db.cursor()) as cr:
            cmd = "SELECT d.datname as saasmaster_v14,pg_catalog.pg_get_userbyid(d.datdba) as Owner FROM pg_catalog.pg_database d;"
            cr.execute(cmd)
            rows = cr.fetchall()
        owner = None
        for row in rows:  # Getting Saasmaster owner
            if row[0] == saas_db_name:
                owner = row[1]
        config = odoo.tools.config
        tenant_db_list_obj = self.env['tenant.database.list']
        tenant_db = self.db_name
        cr = self._cr
        db_name = self.db_name.name
        expiry_date_str = str(self.db_name.exp_date).split("-")
        exp_date = datetime(int(expiry_date_str[0]), int(expiry_date_str[1]), int(expiry_date_str[2]))
        today = datetime.today()
        if exp_date > today:
            try:
                cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': db_name, 'role': owner})
            except Exception as e:
                raise exceptions.except_orm(_("Error!"), _(e))

            stage_ids = self.env['tenant.database.stage'].search([('is_active', '=', True)])
            tenant_db.write({'expired': False,
                             'stage_id': stage_ids[0].id if stage_ids else False})
            cr.commit()
        else:
            raise exceptions.except_orm(_("Warning!"), _('Sorry, you can not activate the Database...!'))
        return {
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'tenant.database.list',
            'context': self._context,
            'type': 'ir.actions.act_window',
        }

    def terminate_db(self):
        """
        1. Set tenant DB stage to Purge
        2. Inactive all agreements related to this db
        3. Drop the DB
        """
        config = odoo.tools.config
        tenant_db_list_obj = self.env['tenant.database.list'].sudo()
        agreement_obj = self.env['sale.recurring.orders.agreement'].sudo()

        tenant_db = self.db_name
        db_name = self.db_name.name
        db_id = self.db_name.id
        cr = self._cr
        ##deactivate DB
        stage_ids = self.env['tenant.database.stage'].search([('is_purge', '=', True)])
        tenant_db.write({'stage_id': stage_ids[0].id if stage_ids else False})
        ##deactivate agreements
        agreement_ids = agreement_obj.search([('order_line.order_id.instance_name', '=', str(db_name))])

        agreement_ids.write({'active': False})

        # cr.execute("""UPDATE pg_database SET datallowconn = 'false' WHERE datname = '%s';"""%db_name)
        # cr.execute("""ALTER DATABASE %s CONNECTION LIMIT 1;"""%db_name)

        cr.execute("""SELECT pg_terminate_backend(pid) 
 FROM pg_stat_get_activity(NULL::integer) 
 WHERE datid=(SELECT oid from pg_database where datname = '%s');""" % db_name)

        cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': tenant_db.name, 'role': 'expired_db_owner'})

        return {
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'tenant.database.list',
            'context': self._context,
            'type': 'ir.actions.act_window',
        }

        ##Don't drop Database, just move to Terminated stage

        ##drop DB
        try:
            cr.execute("ALTER DATABASE %(db)s OWNER TO %(role)s" % {'db': db_name, 'role': config['db_user']})
        except Exception as e:
            trace_str = str(traceback.format_exc())
            raise exceptions.except_orm(_("Error!"), _(str(e) + "\n " + trace_str))

        print(11111111111111111111111111111111111111)

        db = odoo.sql_db.db_connect('postgres')
        with closing(db.cursor()) as cr:
            cr.autocommit(True)  # To avoid transaction block
            # _drop_conn(cr, db_name)

            # Try to terminate all other connections that might prevent
            # dropping the database
            print(2222222222222222222222222222222222)
            try:
                pid_col = 'pid' if cr._cnx.server_version >= 90200 else 'procpid'

                #                 cr.execute("""SELECT pg_terminate_backend(%(pid_col)s)
                #                               FROM pg_stat_activity
                #                               WHERE datname = %%s AND
                #                                     %(pid_col)s != pg_backend_pid()""" % {'pid_col': pid_col},
                #                            (db_name,))
                #                 cr.execute("""select pg_terminate_backend(pid) from pg_stat_activity where datname='%s';"""%(db_name,))

                cr.execute("""UPDATE pg_database SET datallowconn = 'false' WHERE datname = '%s';""" % db_name)
                cr.execute("""ALTER DATABASE %s CONNECTION LIMIT 1;""" % db_name)

                cr.execute("""SELECT pg_terminate_backend(pid) 
 FROM pg_stat_get_activity(NULL::integer) 
 WHERE datid=(SELECT oid from pg_database where datname = '%s');""" % db_name)

                print(333333333333333333333333333333333333333333)
                print(db_name, '+________________________________dbbbbbbbbb')
                cr.execute("DROP DATABASE %s" % db_name)
                print(444444444444444444444444444444444444444444444)
            except Exception as e:
                trace_str = str(traceback.format_exc())
                raise Exception("Couldn't drop database %s: %s" % (db_name, str(e) + "\n\n" + trace_str))

            print(55555555555555555555555555555555)

        print(6666666666666666666666666666666666666666666)
        # db.exp_drop(db_name)
        return {
            'view_type': 'kanban',
            'view_mode': 'kanban',
            'res_model': 'tenant.database.list',
            'context': self._context,
            'type': 'ir.actions.act_window',
        }


# (db_controll_wizard)

class update_tenants(models.TransientModel):
    _name = 'update.tenants.wizard'
    _description = 'Update Tenants stages'

    #     def update_tenants(self, cr, uid, ids, data, conText=None):
    #         tenant_db_list_obj = self.pool.get('tenant.database.list')
    #         tenant_ids = tenant_db_list_obj.search(cr, uid, [('stage_id', '=', False)])
    #         for tenant in tenant_db_list_obj.browse(cr, uid, tenant_ids):
    #             if tenant.free_trial:
    #                 active_stage_id = self.pool.get('tenant.database.stage').search(cr, uid, [('is_active', '=', True)])
    #                 tenant_db_list_obj.write(cr, uid, [tenant.id], {'stage_id':active_stage_id[0] if active_stage_id else False}, conText)
    #
    #             if tenant.expired:
    #                 active_stage_id = self.pool.get('tenant.database.stage').search(cr, uid, [('is_expired', '=', True)])
    #                 tenant_db_list_obj.write(cr, uid, [tenant.id], {'stage_id':active_stage_id[0] if active_stage_id else False}, conText)
    #
    #         return { 'type':'ir.actions.act_window_close' }
    #
    def update_tenants(self):
        tenant_db_list_obj = self.env['tenant.database.list']
        tenant_ids = tenant_db_list_obj.search([('stage_id', '=', False)])
        for tenant in tenant_ids:
            if tenant.free_trial:
                active_stage_id = self.env['tenant.database.stage'].search([('is_active', '=', True)], limit=1)
                tenant.write({'stage_id': active_stage_id.id if active_stage_id else False})

            if tenant.expired:
                active_stage_id = self.env['tenant.database.stage'].search([('is_expired', '=', True)], limit=1)
                tenant.write({'stage_id': active_stage_id.id if active_stage_id else False})

        return {'type': 'ir.actions.act_window_close'}
