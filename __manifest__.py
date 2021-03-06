# -*- coding: utf-8 -*-
{
    'name': "Products",
    'icon': '/products/static/src/description/icon.png',
    'version': '0.2',
    'category': 'Products',
    'summary': 'Import products and their details from EAN file',
    'depends': ['product', 'base', 'web'],
    'data': [
        'views/views.xml',
        'views/tree_view_asset.xml',
        'views/cron.xml',
    ],
    'qweb': ['static/src/xml/tree_view_button.xml'],
    # 'demo': [
    # ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
