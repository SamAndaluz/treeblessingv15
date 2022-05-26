
from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from werkzeug import urls
import logging

_logger = logging.getLogger(__name__)

odoo_request = request

try:
    import pagseguro
except ImportError:
    _logger.warning("Não é possível importar pagseguro", exc_info=True)
from pagseguro import PagSeguro


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[('pagseguro', 'Pagseguro')], ondelete={'pagseguro': 'set default'})
    pagseguro_email_account = fields.Char('Pagseguro Email', required_if_provider='pagseguro',
                                          groups='base.group_user')
    pagseguro_token = fields.Char('Pagseguro Token', groups='base.group_user',
                                  help='The Pagseguro Token is used to ensure communications coming from Pagseguro'
                                       ' are valid and secured.')

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'pagseguro':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_pagseguro.payment_method_pagseguro').id

    def _pagseguro_prepare_pagseguro_object(self):
        """ Make a request at pagseguro endpoint.

        Note: self.ensure_one()

        :return pagseguro Object
        :rtype: object
        """
        self.ensure_one()
        if self.state == 'test':
            config = {'sandbox': True}
        else:
            config = {'sandbox': False}
        pg = PagSeguro(email=self.pagseguro_email_account, token=self.pagseguro_token, config=config)
        return pg