{
    'name': "Integração Correios",
    'summary': """Integração com os Correios""",
    'description': """Módulo para gerar etiquetas de rastreamento de \
encomendas""",
    'version': '15.0.1.0.0',
    'category': 'Sale',
    'author': 'Trustcode',
    'license': 'Other OSI approved licence',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        "Felipe Paloschi <paloschi.eca@gmail.com>"
    ],
    'depends': [
        'stock', 'delivery'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_correios_data.xml',
        'views/correios.xml',
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/stock_picking.xml',
        'reports/shipping_label.xml',
        'reports/plp_report.xml',
    ],
    'application': True,
    'installable': True,
}
