# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import SUPERUSER_ID as ADMINUSER_ID
from odoo import http
from odoo import api, fields, models
import json
import re
import datetime
#from odoo import pooler
from odoo import tools
#from odoo import pooler
from odoo.addons.web.controllers import main
import werkzeug.utils
import werkzeug.wrappers
from odoo.tools import config











class website_sale(http.Controller):

    @http.route(['/web/check_for_superuser'], type='http', auth="none", csrf=False)
    def check_for_superuser(self,  **post):
        values = {}
        values['user'] = request.session.uid
        return json.dumps(values)
    
    
#     @http.route(['/web/check_for_superuser'], type='json', methods=['GET', 'POST'], auth="public", website=True)
#     def check_for_superuser(self, **kw):
#         print (request.session.uid,'=========')
#         return request.session.uid
        
        
        
        
        
        
        
        
        
        
        