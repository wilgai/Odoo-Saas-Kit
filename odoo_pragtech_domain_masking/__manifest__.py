{
    'name': 'SaaS-Master/SaaS-Tenant:Domain Masking',
    'version': '13.0.0',
    'category': 'SaaS',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'summary': 'SaaS-Master/SaaS-Tenant:Domain Masking software as a service odoo saas pragmatic saas Saaskit saas script software odoo saas odoo saaskit odoo saaskit software pragmatic saaskit saas pack cloud Odoo SaaS Kit odoo_saas_kit saas business',
    'depends': ['saas_base'],
    'description': """
This module helps to add a separate domain name to the tenant database url. If tenant has their own domain registered and wish to access Odoo tenant database using their own domain, then this module helps to do the same. Technically this is called domain masking.
""",
    'data': [
        'views/base_admin_view.xml',
        'views/res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/animated-domain-masking.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=310&name=support-domain-masking-saas-kit',
    'price': 300,
    'currency': 'USD',
    'license': 'OPL-1',
    'application': True,
    'auto_install': False,
    'installable': True,
}
