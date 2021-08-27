{
    'name': 'SaaS-Tenant:',
    'version': '1.0',
    'category': 'SaaS',
    'description': """Openerp SAAS Tenant Restriction Module """,
    'author': 'Pragmatic TechSoft Pvt. Ltd.',
    'depends': ['openerp_saas_tenant',],
    'data': [
        'security/saas_service_security.xml',
        'security/ir.model.access.csv',
        'views/template.xml',
        # 'views/users_view.xml',
        # 'vies/account_bank_view.xml',
    ],
    'qweb': [
        # 'static/src/xml/base.xml',
    ],

    'installable': True,
    'active': True,
}
