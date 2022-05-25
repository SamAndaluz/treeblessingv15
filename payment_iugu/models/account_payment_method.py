# -*- coding: utf-8 -*-

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)

try:
    import iugu
except ImportError:
    _logger.warning("Não é possível importar iugu", exc_info=True)


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['iugu'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res