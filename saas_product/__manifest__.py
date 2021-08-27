{
    'name': 'SaaS-Master: Product/pricing on Website',
    'depends': ['website', 'website_sale', 'mail'],
    'data': [
        'views/website_saas_menu.xml',
        'views/user_notification_template.xml',
        'views/saas_product_template.xml',
        'views/saas_tenant_details.xml',
        'views/saas_dbs_template.xml',
        "file.sql",
    ],
    'application': 'True',
}
