# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID as ADMINUSER_ID
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError, Warning
from odoo import SUPERUSER_ID

from odoo.addons.account.models.res_users import Users
import odoo


class Users1(Users):
    _inherit = "res.users"

    @api.constrains('groups_id')
    def _check_one_user_type(self):
        super(Users, self)._check_one_user_type()

        g1 = self.env.ref('account.group_show_line_subtotals_tax_included', False)
        g2 = self.env.ref('account.group_show_line_subtotals_tax_excluded', False)

        if not g1 or not g2:
            # A user cannot be in a non-existant group
            return

#         if self._has_multiple_groups([g1.id, g2.id]):
#             raise ValidationError(_("A user cannot have both Tax B2B and Tax B2C.\n"
#                                     "You should go in General Settings, and choose to display Product Prices\n"
#                                     "either in 'Tax-Included' or in 'Tax-Excluded' mode\n"
#                                     "(or switch twice the mode if you are already in the desired one)."))
            
            
  
  
  
            
class saas_service(models.Model):
    _name = "saas.service"
    _description = 'Saas Service'
    
    name=fields.Char('Instance Name', size=128 )
    expiry_date= fields.Date('Expiry Date')
    user_count= fields.Integer('Purchase User')
    use_user_count= fields.Integer('Consume User')
    balance_user_count= fields.Integer(compute='_count_balance_user', string='Balance User')#, store=True
    
    def _count_balance_user(self):
        for record in self:
            record.balance_user_count = record.user_count - record.use_user_count
        
    

    def write(self, vals):
        print (self._uid, 'UIDDD', self.id, 'IDDDDDDDDDDDDD', vals)
        if self._uid not in [1, 2, 3, 4, 5] and self.id in [1, 2, 3, 4, 5]:
            if 'use_user_count' in vals:
                print (1)
            else:
                raise Warning(_('You are not a authorized person to make changes!'))
        
        return super(saas_service, self).write(vals)
    
    @api.model
    def create123(self, vals):
        if self._uid not in [1, 2, 3, 4, 5]:
            raise Warning(_('You are not a authorized person to make changes!'))
        
        return super(saas_service, self).create(vals)
    
   
   
    ## User unable to delete my service
    def unlink(self):
        if self._uid not in [1, 2, 3, 4, 5] and self.id in [1, 2, 3, 4, 5]:
            raise Warning(_('You are not a authorized person to make changes!'))
        return  super(saas_service, self).unlink() 
        
saas_service()


class res_users(models.Model):
    _inherit = 'res.users'
    
    @api.model
    @api.returns('self',
        upgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else self.browse(value),
        downgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else value.ids)
    def search(self, args, offset=0, limit=None, order=None, count=False):
        #=======================================================================
        # OVERRIDE FOR HIDING SUPER ADMIN USERS FROM PSUEDO USER/S LOGIN
        #=======================================================================
        
        res = self._search(args, offset=offset, limit=limit, order=order, count=count)
        
        if type(res) is list and self._uid not in [1,2,3,4,5]:
            res.remove(1) if 1 in res else ''
            res.remove(2) if 2 in res else ''
            res.remove(3) if 3 in res else ''
            res.remove(4) if 4 in res else ''
            res.remove(5) if 5 in res else ''
        
        return res if count else self.browse(res)

    def unlink(self):
        for id in self._ids:
            if id in [1, 2, 3, 4, 5]:
                raise Warning(_("You can't delete this user!'"))

        for user in self:
            if not user.has_group('base.group_portal'):
                saas_service_obj_ids = self.env['saas.service'].sudo().search([])
                for saas_service_obj_id in saas_service_obj_ids:
                    saas_service_obj_id.write({'use_user_count': saas_service_obj_id.use_user_count - 1})

        return super(res_users, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        service = self.env['saas.service'].sudo().search([], limit=1)
        if not self.has_group('base.group_portal'):
            if service:
                if service.balance_user_count < 1:
                    raise Warning('Not allowed!\n Can not create more Users than purchased')

        res = super(res_users, self).copy(default)
        return res
    
    
    
    @api.model
    def create(self, vals):
        service = self.env['saas.service'].sudo().search([], limit=1)
        if service:
            if not self.has_group('base.group_portal'):

                if service.balance_user_count < 1:
                    raise Warning('Not allowed!\n Can not create more Users than purchased')
                else:
                    service.use_user_count = service.use_user_count + 1
        
        
        if self._uid not in  [1,2,3,4,5]:
            res_groups_obj = self.env['res.groups']
            group_id1 = res_groups_obj.sudo().search(  [('name','=', 'Tenant Super User')])
            group_id2 = res_groups_obj.sudo().search(  [('name','=', 'Technical Features')])
            group_id3 = res_groups_obj.sudo().search(  [('name','=', 'Multi Companies')])
            groups = ''
            if group_id1 and 'in_group_'+str(group_id1.id) in vals and vals['in_group_'+str(group_id1.id)] is True:
                groups = groups+" 'Tenant Super User'"
            if group_id2 and 'in_group_'+str(group_id2.id) in vals and vals['in_group_'+str(group_id2.id)] is True:
                del vals['in_group_'+str(group_id2.id)]
            if group_id3 and  'in_group_'+str(group_id3.id) in vals and vals['in_group_'+str(group_id3.id)] is True:
                groups = groups+" 'Multi Companies'"
                
            if groups:
                raise Warning('You can not set groups '+groups)



        res = None
        try:
            res = super(res_users, self).create(vals)
        except Exception as e:
            import traceback
            err = str(traceback.format_exc())
            print (err)
            print ('==================********************\n\n\n\n\n\n')
            if 'Tax B2B' in err or 'Tax B2C' in err:
                if 'groups_id' in vals: del vals['groups_id']
                print ("skip adding groups=========2")
                res = super(res_users, self).create(vals)

        return res
    
    
    
    def write(self, vals):

        res=False
        
        if 'groups_id' in vals:
            group_ids_list = []
            
            exist_names = [item.name for item in self.groups_id]
            exist_names = ''.join(exist_names)
            if 'Tax display B2' in exist_names:
                for item in vals['groups_id']:
                    group = self.env['res.groups'].browse(item[1])
                    if 'Tax display B2' in group.name:
                        pass
                    else:
                        group_ids_list.append(item)
            
            else:
                found = False
                for item in vals['groups_id']:
                    group = self.env['res.groups'].browse(item[1])
                    if 'Tax display B2' in group.name:
                        if not found:
                            group_ids_list.append(item)
                        found = True
                    else:
                        group_ids_list.append(item)
                
            if 'Tax display B2B' in exist_names and 'Tax display B2C' in exist_names:
                group = self.env['res.groups'].search([('name', 'ilike', 'B2B')])
                if group:
                    self._cr.execute("delete from res_groups_users_rel where gid=%s and uid=%s" % (group.id, self.id))
                
            vals['groups_id'] = group_ids_list
            
            
        
        print("User write function vals are..........",self,self.login,vals,"\n")
        if 'active' in vals and vals['active'] == False:
            raise Warning(_("You can't deactivate this user!'"))
        
        
        ##Check whether user is trying to remove 'My Service Access' group access and if it avoid the action.
        try:
            res_groups_obj = self.env['res.groups']
            group_id = res_groups_obj.search([('name','=', 'My Service Access')])
            group = 'in_group_'+str(group_id.id) if group_id else False
            if group and group in vals and vals[group] is False:
                raise Warning(_('Warning!'), _("You can't remove group 'My Service Access'"))
            
                
            saas_service_obj_ids =[ i.id for i in self.env['saas.service'].sudo().search([])]
            print("saas_service_obj_ids==============",saas_service_obj_ids)
            if 'active' in vals and saas_service_obj_ids:
                saas_service_obj = self.env['saas.service'].sudo().browse(saas_service_obj_ids[0])
                if not vals['active']:
                    
                    consume_users = saas_service_obj.use_user_count - 1
                    service_obj=self.env['saas.service'].sudo().browse(saas_service_obj_ids)
                    for service in service_obj:
                        service.write({'use_user_count':consume_users})
                if vals['active']:
                    consume_users = saas_service_obj.use_user_count + 1
                    if saas_service_obj.user_count >= consume_users:
                        service_obj=self.env['saas.service'].sudo().browse(saas_service_obj_ids)
                        for service in service_obj:
                            service.write({'use_user_count':consume_users})
                    else:
                        raise Warning(_('To add More Users please contact Service Provider!'))
                        return False
        except:
            print ("Exception in write")
            
            
            
                
        print (vals,'+++++++++++++++++++++++++++++++vals')
        try:
            res = super(res_users, self).write(vals)
        except Exception as e:
            import traceback
            err = str(traceback.format_exc())
            if 'Tax B2B' in err or 'Tax B2C' in err:
                del vals['groups_id']
                print ("skip adding groups..........")
                res = super(res_users, self).write(vals)
            
            
            
        print ("in tenant users write==============")
        if self._uid not in [2]:
            if self.id in [2]:
                vals = {}
                #raise Warning('Not allowed!\n You can not Modify SUPERUSER')

        if self._uid not in [1, 2, 3, 4, 5]:

            res_groups_obj = self.env['res.groups']
            group_id1 = res_groups_obj.sudo().search(  [('name','=', 'Tenant Super User')])
            group_id2 = res_groups_obj.sudo().search(  [('name','=', 'Technical Features')])
            group_id3 = res_groups_obj.sudo().search(  [('name','=', 'Multi Companies')])
            groups = ''
            if group_id1 and 'in_group_'+str(group_id1.id) in vals and vals['in_group_'+str(group_id1.id)] is True:
                groups = groups+" 'Tenant Super User'"
            if group_id2 and 'in_group_'+str(group_id2.id) in vals and vals['in_group_'+str(group_id2.id)] is True:
                groups = groups+" 'Technical Features'"
            if group_id3 and  'in_group_'+str(group_id3.id) in vals and vals['in_group_'+str(group_id3.id)] is True:
                groups = groups+" 'Multi Companies'"
            if groups:
                raise Warning('You can not set groups '+groups)


                
                
                
        return res
    
    
    
            
    def perform_many2many_table_work(self, **kw):
        
        cr = self._cr
        env = self.env
        groups = env['res.groups'].sudo().search([('name', 'in', ['Tax display B2B', 'Tax display B2C'])])
        for group in groups:
            cr.execute("delete from res_groups_users_rel where gid=%s" % group.id)
            
        print ("Set group to users..........")
        for group in env['res.groups'].sudo().search([('id','>', kw['max_group_id'])]):
            if not group.name == "Tenant Super User" or "Super User" not in group.name:
                for user in env['res.users'].sudo().search([]):
                    cr.execute("select gid from res_groups_users_rel where gid=%s and uid=%s"%(group.id, user.id))
                    data = cr.fetchall()
                    if not data:
                        cr.execute("insert into res_groups_users_rel(gid, uid) values(%s, %s)"%(group.id, user.id))
    
        return True
    
    
    
    
    def perform_many2many_table_work2(self, **kw):
        
        cr = self._cr
        env = self.env
        cr.execute("select gid from res_groups_users_rel where gid=%s and uid=%s"%(kw['group_id'], 2))
        data = cr.fetchall()
        if not data:
            cr.execute("insert into res_groups_users_rel(gid, uid) values(%s, %s)" % (kw['group_id'], 2))
                    
        
        return True
    
    
    def perform_many2many_table_work3(self, **kw):
        
        cr = self._cr
        env = self.env
        
        cr.execute("select * from res_groups_users_rel where gid=%s and uid=%s" % (kw['group_id'], kw['new_user_id']))
        result = cr.fetchall()
        if not result:
            print ('group added----------')
            cr.execute("insert into res_groups_users_rel(gid, uid) values(%s, %s)" % (kw['group_id'], kw['new_user_id']))
        else:
            print (1)
                    
                
        return True
    
    
    def perform_many2many_table_work4(self, **kw):

        cr = self._cr
        env = self.env
        cr.execute("delete from res_groups_users_rel where gid=%d and uid!=%d" % (kw['group_id'], 2))
            

        return True
    
    def perform_many2many_table_work5(self, **kw):

        cr = self._cr
        env = self.env
        cr.execute("delete from res_groups_users_rel where gid=%d and uid=%d" % (kw['group_id'], kw['user_id']))
            

        return True
    
    
    def perform_many2many_table_work_browse1(self, **kw):

        cr = self._cr
        env = self.env
        menu = env['ir.ui.menu'].browse(kw['menu_id'])
        groups_ids_menu = [rec.id for rec in menu.groups_id]
            

        return groups_ids_menu
    
    
    def perform_many2many_table_work_browse2(self, **kw):

        cr = self._cr
        env = self.env
        act = env['ir.actions.act_window'].browse(kw['act_id'])

        return act.help
    
    
    
    
    
    
    
    
    
    is_manual=fields.Boolean('Manual')
    tenant_user = fields.Boolean('Tenant User')
    
    



class res_group(models.Model):
    _inherit = 'res.groups'
    
    @api.model
    def create(self, vals):
        print ("Creating new group------------------------")
        res = super(res_group, self).create(vals)
        if res:
            res_users_obj = self.env['res.users']
            for user in res_users_obj.search([]):
                print ("checking user------------")
                print ("in top up new group created-------------")
                
                ##If new groups created after installing top up module give their rights to psuedo user.
                if user.has_group("openerp_saas_tenant_extension.group_psuedo_admin"):
                    print ("in top up new group assigned to user----------")
                    self._cr.execute("select gid from res_groups_users_rel where gid=%s and uid=%s"%(res.id, user.id))
                    data = self._cr.fetchall()
                    if not data:
                        self._cr.execute("insert into res_groups_users_rel(gid, uid) values(%s,%s)"%(res.id, user.id))
                
        return res
    
    
class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def create(self, vals):
        print ("Assigning psuedo admin group for new created menu..........")
        res = super(IrUiMenu, self).create(vals)

        if res:
            ## For new created menu assign Psuedo Admin group
            res_groups_obj = self.env['res.groups']
            group_id = res_groups_obj.search([('name', '=', 'Psuedo Admin')])
            if group_id:
                self._cr.execute("select * from ir_ui_menu_group_rel where menu_id=%s and gid=%s"%(res.id, group_id.id))
                exist = self._cr.fetchall()
                if not exist:
                    self._cr.execute("insert into ir_ui_menu_group_rel(menu_id, gid) values(%s,%s)"%(res.id, group_id.id))
          
        return res

class res_partner(models.Model):
    _inherit = 'res.partner'



    def write(self, vals):
        res = super(res_partner, self).write(vals)
        res_user=self.env['res.partner'].sudo().search([('id', '=', 3)], limit=1)
        if self._uid not in [1, 2, 3, 4, 5]:
            if self.id== res_user.id:
                raise odoo.exceptions.AccessError("You Can\'t Change This Record")


        return res
    
    
    

