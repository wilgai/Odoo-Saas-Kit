import odoo
from odoo import api, fields, models 
from odoo import SUPERUSER_ID as ADMINUSER_ID
import logging
from urllib.parse import urljoin
import werkzeug
from odoo.tools import config
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    
    _inherit = "res.partner" 
    
    
    @api.depends('company_name', 'parent_id.is_company', 'commercial_partner_id.name')
    def _compute_commercial_company_name(self):
        for partner in self:
            p = partner.commercial_partner_id
            partner.commercial_company_name = p.is_company and p.name or partner.company_name
    
    
    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

    
    commercial_company_name = fields.Char('Company Name Entity', compute='_compute_commercial_company_name',
                                          store=True)
    
    commercial_company_name = fields.Char('Company Name Entity', compute='_compute_commercial_company_name',
                                          store=True)
#     def _search(self, cr, user, args, offset=0, limit=None, order=None, conText=None, count=False, access_rights_uid=None):
    
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        conText = self._context#dict(conText or {}, active_test=False)
#         if not args:
#             args = []
        
        support_contact_id = 0   
        res_id = models.Model._search(self, args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
#         print "res_id---------------",res_id
        get_contact_obj = self.browse(res_id) 
#         print "get_contact_obj------------",get_contact_obj
        ICPSudo = self.env['ir.config_parameter'].sudo()
        brand_name = ICPSudo.search([('key', '=', 'brand_name')]).value
        for contact_obj in get_contact_obj:
            if contact_obj.name == brand_name :
                support_contact_id = contact_obj.id


            if support_contact_id:
                if self._uid != 2:
                    res_id = [x for x in res_id if x != support_contact_id]
                    #             print "completed res_id---------------"
                    return res_id
            
            
        else :
            return res_id
            
        
    
    
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None, conText=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        if conText is None:
            conText= {}
        res = dict.fromkeys(self.ids, False)
        # base_url = "http://"+('localhost:1999')
        base_url = self.get_base_url()

         
        for partner in self:
            # when required, make sure the partner has a valid signup token
            if conText.get('signup_valid') and not partner.user_ids:
                self.signup_prepare([partner.id])
                base_url = partner.get_base_url()
 
            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self._cr.dbname)
            signup_type = conText.get('signup_force_type_in_url', partner.signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type
 
            if partner.signup_token and signup_type:
                query['token'] = partner.signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
            else:
                continue        # no signup token, no user, thus no signup url!
 
            fragment = dict()
            if action:
                fragment['action'] = action
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['id'] = res_id
 
            if fragment:
                query['redirect'] = '/web#' + werkzeug.url_encode(fragment)
 
            res[partner.id] = urljoin(base_url, "/web/%s?%s" % (route, werkzeug.url_encode(query)))
             
        print ("--------------------------------------------------------------------",res)
        return res
    
    
