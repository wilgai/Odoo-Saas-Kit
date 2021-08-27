
from odoo import api, fields, models
import odoo
from odoo.api import Environment

class bank_ac(models.Model):
    _inherit = "ir.model"

    def init(self):
        print("innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",self._cr)
        # tenant_cr = tenant_db.cursor()
        # models = [
        #     'res.groups'
        #
        # ]
        #
        # except_groups = [
        #     'Tenant Super User']
        #
        # query = """
        #             update ir_model_access
        #             set  perm_read = True, perm_write = False, perm_unlink = False, perm_create = False
        #             where
        #             group_id not in (select id from res_groups where name in
        #             %s)
        #             and model_id in (select id from ir_model where model in %s)
        #         """
        # self._cr.execute(query, (tuple(except_groups), tuple(models)))




    # self._cr.execute("update ir_model_access set  perm_read = True, perm_write = False, perm_unlink = False, perm_create = False where  group_id not in (select id from res_groups where name in %s) and model_id in (select id from ir_model where model in %s)" %(tuple(except_groups), tuple(models)))



