from odoo import models, fields


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(
        selection_add=[('correios', 'Correios')])
