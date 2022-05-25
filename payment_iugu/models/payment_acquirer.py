
from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from werkzeug import urls
import logging

_logger = logging.getLogger(__name__)

odoo_request = request

try:
    import iugu
except ImportError:
    _logger.warning("Não é possível importar iugu", exc_info=True)


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    def _default_return_url(self):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        return "%s%s" % (base_url, "/payment/status")

    provider = fields.Selection(selection_add=[("iugu", "Iugu")], ondelete={'iugu': 'set default'})
    iugu_api_key = fields.Char("Iugu Api Token")
    return_url = fields.Char(string="Url de Retorno", default=_default_return_url, size=300)

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'iugu':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_iugu.payment_method_iugu').id

    def _iugu_make_request(self, data=None, method='POST', invoice_id=False):
        """ Make a request at Iugu endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict data: The payload of the request
        :param str method: The HTTP method of the request
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()
        iugu.config(token=self.iugu_api_key)
        invoice = iugu.Invoice()
        if not invoice_id :
            result = invoice.create(data)
        else:
            result = invoice.search(invoice_id)
        if "errors" in result:
            if isinstance(result["errors"], str):
                msg = result['errors']
            else:
                msg = "\n".join(
                    ["A integração com IUGU retornou os seguintes erros"] +
                    ["Field: %s %s" % (x[0], x[1][0])
                     for x in result['errors'].items()])
            raise UserError(msg)
        return result
