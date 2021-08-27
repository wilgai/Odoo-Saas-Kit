{
    'name': 'SaaS-Tenant:SaaS Tenant',
    'version': '1.0',
    'category': 'SaaS',
    'description': """Openerp SAAS Tenant Restriction Module """,
    'author': 'Pragmatic TechSoft Pvt. Ltd.',
    'depends': ['base', 'sales_team'],
    'data': [
        'security/saas_service_security.xml',
        'views/openerp_saas_tenant_view.xml',
        'views/users_view.xml',
        # 'ir_actions_view.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'static/src/xml/template.xml',

    ],
    'installable': True,
    'active': False,
}
