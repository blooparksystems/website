{
    'name': 'eCommerce SEO Optimized',
    'category': 'Website',
    'sequence': 55,
    'summary': 'Sell Your Products Online',
    'website': 'http://www.bloopark.de',
    'version': '1.0',
    'description': """
OpenERP E-Commerce SEO Optimized
==================

        """,
    'depends': [ 'website_sale',],
    'data': [
        'views/templates.xml',
    ],
    'demo': [
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
}
