# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
import time
# from mx.DateTime import RelativeDateTime
# import mx.DateTime
from odoo.tools import config
import logging
from odoo.service import db
import odoo.addons.decimal_precision as dp
from odoo import SUPERUSER_ID
import datetime
import base64
# import pycurl
import os
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


#=============================================================================
# Warning : Don't edit or change the below string
#=============================================================================
file_string_static = """<VirtualHost *:80>
    ServerName xyz_domain_name
    RewriteEngine On
    RewriteCond %{HTTP_HOST} ^xyz_domain_name$ [OR]
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>
<VirtualHost *:443>
    ServerName xyz_domain_name
    RewriteEngine On    
    ProxyRequests On
    KeepAliveTimeout 2400
    ProxyPreserveHost on
    ProxyVia On
    Timeout 2400
    ProxyTimeout 2400
    ProxyBadHeader Ignore
    Keepalive On
    SSLEngine On
    SSLProxyEngine on
    SSLProxyCheckPeerCN on
    SSLProxyCheckPeerExpire on
    RequestHeader set Front-End-Https "On"
    SSLCertificateFile ssl1
    SSLCertificateKeyFile ssl2
    SSLCertificateChainFile ssl3
    ErrorLog ${APACHE_LOG_DIR}/sslerror.log    
    <Proxy *>
        AddDefaultCharset off
                Order deny,allow
                Allow from all
    </Proxy>
    ProxyPass / http://localhost:8069/ retry=1 acquire=3000 Keepalive=On
    ProxyPassReverse / http://localhost:8069/
    ProxyPreserveHost Off
    LogLevel warn
    SetEnv proxy-sendchunked  1
</VirtualHost>
"""


file_string_static_http = """
<VirtualHost *:80>
ServerName xyz_domain_name
ProxyRequests off
ProxyVia On
<Proxy *>
Order deny,allow
Allow from all
</Proxy>

ProxyPass / http://localhost:8069/ retry=1 acquire=3000 timeout=600 Keepalive=On
ProxyPassReverse / http://localhost:8069/
</VirtualHost>
"""


class tenant_database_list(models.Model):
    _inherit = "tenant.database.list"

    # @api.multi
    def action_restart_apache(self):
        try:
            os.system('sudo /etc/init.d/apache2 restart')
        except:
            raise ValidationError(_('Something goes wrong, Please try again'))
        return True



    # @api.multi
    def action_remove_client_domain(self):
        ##Edit config file and remove needed data block
        ICPSudo = self.env['ir.config_parameter'].sudo()
        apache_ssl_path = ICPSudo.search([('key', '=', 'apache_ssl_path')]).value,
        apache_config_file = ICPSudo.search([('key', '=', 'apache_config_file')]).value,
        if type(apache_ssl_path) is tuple:
            apache_ssl_path = apache_ssl_path[0]
        if type(apache_config_file) is tuple:
            apache_config_file = apache_config_file[0]

        f = open(apache_config_file, 'r+')



            # domain = self.domain_masking_fields.client_domain


        file_string = file_string_static
        file_string = file_string.replace('xyz_domain_name', self.domain_masking_fields.client_domain)
        file_string = file_string.replace('ssl1', apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl1_filename)
        file_string = file_string.replace('ssl2', apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl2_filename)
        file_string = file_string.replace('ssl3', apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl3_filename)

        file_data = str(f.read())
        file_data = file_data.replace(file_string, '')

        f.seek(0)
        f.truncate()

        f.write(file_data)

        ##Delete files from their locations
        try:
            os.unlink(apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl1_filename)
            os.unlink(apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl2_filename)
            os.unlink(apache_ssl_path+"/"+self.name+"_"+self.domain_masking_fields.client_ssl3_filename)
        except:
            print ("Some error!")

        self.domain_masking_fields.using_domain = False
        self.virtual_text_block = ''

        return True




    def validate_cirtificate(self, file_path, url):
        print ("Validating certificate ------")
#         try:
#             curl = pycurl.Curl()
#             curl.setopt(pycurl.CAINFO, file_path)
#             curl.setopt(pycurl.SSL_VERIFYPEER, 1)
#             curl.setopt(pycurl.SSL_VERIFYHOST, 2)
#             curl.setopt(pycurl.URL, url)
#             curl.perform()
#         except:
#             print ("There is something fishy")
#             raise ValidationError(_('Something is not correct!'))



    def create_file_to_ssl_location(self, data, file):
        file.seek(0)
        file.truncate()

        for line in data:
            print (line)
            if line != "'":
                line = line .replace('b\'', '')
                file.write(line+ "\n")

        return True


    # @api.multi
    def action_set_client_domain(self):
        for domain in self.domain_masking_fields:
            if not domain.client_domain or not domain.client_ssl1 or not domain.client_ssl2 or not domain.client_ssl3:

                raise ValidationError(_("Please fill all Fields!"))


            #=======================================================================
            # Check request is already added/activated or not
            # if current domain name is found in config file it means it is already added
            #=======================================================================
            ICPSudo = self.env['ir.config_parameter'].sudo()
            apache_ssl_path = ICPSudo.search([('key', '=', 'apache_ssl_path')]).value,
            apache_config_file = ICPSudo.search([('key', '=', 'apache_config_file')]).value,

            if not apache_ssl_path:
                raise ValidationError('Apache ssl path is not configured')
            if not apache_config_file:
                raise ValidationError('Apache config file is not configured')

            if type(apache_ssl_path) is tuple:
                apache_ssl_path = apache_ssl_path[0]
            if type(apache_config_file) is tuple:
                apache_config_file = apache_config_file[0]

            f = open(apache_config_file, 'r')
            file_data = str(f.read())
            if domain.client_domain in file_data:
                raise ValidationError(_('Request Already Satisfied, for domain %s.\n To change or edit please deactivate it first.'% domain.client_domain))
            f.close()




            ##Create files on given locations and validate them
            ##---------------Start-------------------
            f1 = open(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl1_filename, 'a+')
            f2 = open(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl2_filename, 'a+')
            f3 = open(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl3_filename, 'a+')

            data = str(base64.b64decode(domain.client_ssl1))
            lines = data.split("\\n")
            self.create_file_to_ssl_location(lines, f1)

            data = str(base64.b64decode(domain.client_ssl2))
            lines = data.split("\\n")
            self.create_file_to_ssl_location(lines, f2)

            data = str(base64.b64decode(domain.client_ssl3))
            lines = data.split("\\n")
            self.create_file_to_ssl_location(lines, f3)

            f1.close()
            f2.close()
            f3.close()

            self.validate_cirtificate(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl1_filename, domain.client_domain)
            self.validate_cirtificate(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl1_filename, domain.client_domain)
            self.validate_cirtificate(apache_ssl_path+"/"+self.name+"_"+domain.client_ssl1_filename, domain.client_domain)
            ##---------------------End---------------------------



            ##Now register entry into configuration file of apache
            f = open(apache_config_file, 'a')

            file_string = file_string_static
            file_string = file_string.replace('xyz_domain_name', domain.client_domain)
            file_string = file_string.replace('ssl1', apache_ssl_path+"/"+self.name+"_"+domain.client_ssl1_filename)
            file_string = file_string.replace('ssl2', apache_ssl_path+"/"+self.name+"_"+domain.client_ssl2_filename)
            file_string = file_string.replace('ssl3', apache_ssl_path+"/"+self.name+"_"+domain.client_ssl3_filename)
            f.write(file_string)

            self.virtual_text_block = file_string
            domain.using_domain = True

        return True






    virtual_text_block = fields.Text("Text Block in Config. File")

    domain_masking_fields = fields.One2many('domain.masking.details','tenant_db_management')


class domain_masking(models.Model):
    _name = "domain.masking.details"
    _description = "Domain Masking"





    client_domain = fields.Char("Client Domain")
    domain_type = fields.Selection([('http', 'HTTP'), ('https', 'HTTPS')], required=True)

    # client_domain_http = fields.Char("Client Domain Http")
    client_ssl1 = fields.Binary("File")
    client_ssl2 = fields.Binary("File")
    client_ssl3 = fields.Binary("File")

    client_ssl1_filename = fields.Char('Domain.key', size=200)
    client_ssl2_filename = fields.Char('Domain.crt', size=200)
    client_ssl3_filename = fields.Char('Domain Chain.crt', size=200)

    using_domain = fields.Boolean("Active Now")
    # virtual_text_block = fields.Text("Text Block in Config. File")

    tenant_db_management = fields.Many2one('tenant.database.list')

    tenant_name=fields.Char('Tenant  Name')





    def action_remove_client_domain(self):
        if self.tenant_name:
            self.tenant_name=False
        ##Edit config file and remove needed data block
        ICPSudo = self.env['ir.config_parameter'].sudo()
        apache_ssl_path = ICPSudo.search([('key', '=', 'apache_ssl_path')]).value,
        apache_config_file = ICPSudo.search([('key', '=', 'apache_config_file')]).value,
        if type(apache_ssl_path) is tuple:
            apache_ssl_path = apache_ssl_path[0]
        if type(apache_config_file) is tuple:
            apache_config_file = apache_config_file[0]

        if self.domain_type == 'https':

            f = open(apache_config_file, 'r+')

            file_string = file_string_static
            file_string = file_string.replace('xyz_domain_name', self.client_domain)
            file_string = file_string.replace('ssl1', apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.client_ssl1_filename)
            file_string = file_string.replace('ssl2', apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.client_ssl2_filename)
            file_string = file_string.replace('ssl3', apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.client_ssl3_filename)

            file_data = str(f.read())
            file_data = file_data.replace(file_string, '')

            f.seek(0)
            f.truncate()

            f.write(file_data)

            ##Delete files from their locations
            try:
                os.unlink(apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.domain_masking_fields.client_ssl1_filename)
                os.unlink(apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.domain_masking_fields.client_ssl2_filename)
                os.unlink(apache_ssl_path+"/"+self.tenant_db_management.name+"_"+self.domain_masking_fields.client_ssl3_filename)
            except:
                print ("Some error!")

            self.using_domain = False
            self.tenant_db_management.virtual_text_block = ''

        else:

            f = open(apache_config_file, 'r+')
            file_string = file_string_static_http
            file_string = file_string.replace('xyz_domain_name', self.client_domain)

            file_data = str(f.read())
            file_data = file_data.replace(file_string, '')

            f.seek(0)
            f.truncate()

            f.write(file_data)

            self.using_domain = False
            self.tenant_db_management.virtual_text_block = ''



        return True





    def action_set_client_domain(self):
        self.tenant_name = self.tenant_db_management.tenant_url

        if self.domain_type == 'https':

            if not self.client_domain or not self.client_ssl1 or not self.client_ssl2 or not self.client_ssl3:

                raise ValidationError(_("Please fill all Fields!"))
        else:
            if not self.client_domain:
                raise ValidationError(_("Please Enter The Domain Name !"))



        #=======================================================================
        # Check request is already added/activated or not
        # if current domain name is found in config file it means it is already added
        #=======================================================================
        ICPSudo = self.env['ir.config_parameter'].sudo()
        apache_ssl_path = ICPSudo.search([('key', '=', 'apache_ssl_path')]).value,
        apache_config_file = ICPSudo.search([('key', '=', 'apache_config_file')]).value,

        if not apache_ssl_path:
            raise ValidationError('Apache ssl path is not configured')
        if not apache_config_file:
            raise ValidationError('Apache config file is not configured')

        if type(apache_ssl_path) is tuple:
            apache_ssl_path = apache_ssl_path[0]
        if type(apache_config_file) is tuple:
            apache_config_file = apache_config_file[0]

        f = open(apache_config_file, 'r')
        file_data = str(f.read())
        if self.client_domain in file_data:
            raise ValidationError(_('Request Already Satisfied, for domain %s.\n To change or edit please deactivate it first.'% self.client_domain))
        f.close()

        if self.domain_type == 'https':
            ##Create files on given locations and validate them
            ##---------------Start-------------------
            f1 = open(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl1_filename, 'a+')
            f2 = open(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl2_filename, 'a+')
            f3 = open(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl3_filename, 'a+')

            data = str(base64.b64decode(self.client_ssl1))
            lines = data.split("\\n")
            self.tenant_db_management.create_file_to_ssl_location(lines, f1)

            data = str(base64.b64decode(self.client_ssl2))
            lines = data.split("\\n")
            self.tenant_db_management.create_file_to_ssl_location(lines, f2)

            data = str(base64.b64decode(self.client_ssl3))
            lines = data.split("\\n")
            self.tenant_db_management.create_file_to_ssl_location(lines, f3)

            f1.close()
            f2.close()
            f3.close()

            self.tenant_db_management.validate_cirtificate(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl1_filename, self.client_domain)
            self.tenant_db_management.validate_cirtificate(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl1_filename, self.client_domain)
            self.tenant_db_management.validate_cirtificate(apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl1_filename, self.client_domain)
            ##---------------------End---------------------------



            ##Now register entry into configuration file of apache
            f = open(apache_config_file, 'a')

            file_string = file_string_static
            file_string = file_string.replace('xyz_domain_name', self.client_domain)
            file_string = file_string.replace('ssl1', apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl1_filename)
            file_string = file_string.replace('ssl2', apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl2_filename)
            file_string = file_string.replace('ssl3', apache_ssl_path+"/"+ self.tenant_db_management.name+"_"+self.client_ssl3_filename)
            f.write(file_string)

            self.tenant_db_management.virtual_text_block = file_string
            self.using_domain = True


        else:

            f = open(apache_config_file, 'a')
            file_string_http = file_string_static_http
            file_string_http = file_string_http.replace('xyz_domain_name', self.client_domain)

            f.write(file_string_http)

            self.tenant_db_management.virtual_text_block= file_string_http
            self.using_domain = True

        return True





















