# -*- coding: utf-8 -*-

{
    'name': 'Pagseguro Payment Acquirer',
    'author': 'Betavision',
    'website': 'https://betavision.com.br',
    'category': 'Accounting',
    'license': 'OPL-1',
    'price': '40',
    'currency': 'EUR',
    'summary': 'Payment Acquirer: Pagseguro Implementation',
    'version': '15.0.1.0.0',
    'description': """Pagseguro Payment Acquirer""",
    'depends': ['payment'],
    'images': ['static/description/payment_pagseguro.jpeg'],
    'data': [
        'views/payment_pagseguro_templates.xml',
        'views/payment_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'external_dependencies': {
        'python': ['pagseguro'],
    },

    'installable': True,
    'auto_install': False,
}
