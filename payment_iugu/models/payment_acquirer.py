
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
        # if not invoice_id :
        #     result = invoice.create(data)
        # else:
        #     result = invoice.search(invoice_id)
        result = {
  "id": "0958D2AAD34049AB889583E26DFA0BF1",
  "due_date": "2017-11-30",
  "currency": "BRL",
  "discount_cents": None,
  "email": "teste@teste.com",
  "items_total_cents": 1000,
  "notification_url": None,
  "return_url": None,
  "status": "pending",
  "tax_cents": None,
  "updated_at": "2014-06-17T09:58:05-03:00",
  "total_cents": 1000,
  "paid_at": None,
  "pix": {
    "qrcode": "https://faturas.iugu.com/iugu_pix/159b70d4-8a7a-492b-bb28-8950d0e9450f-f652/test/qr_codei",
    "qrcode_text": "00020101021226730014br.gov.bcb.pix2551pix.example.com/v2/8b3da2f39a4140d1a91abd93113bd 4415204000053039865406123.455802BR5913Fulano de Tal 6008BRASILIA62190515RP12345678-201963047309"
  },
  "commission_cents": None,
  "secure_id": "0958d2aa-d340-49ab-8895-83e26dfa0bf1-2f4c",
  "secure_url": "http://iugu.com/invoices/0958d2aa-d340-49ab-8895-83e26dfa0bf1-2f4c",
  "customer_id": None,
  "user_id": None,
  "total": "R$ 10,00",
  "taxes_paid": "R$ 0,00",
  "commission": "R$ 0,00",
  "interest": None,
  "discount": None,
  "created_at": "17/06, 09:58 h",
  "refundable": None,
  "installments": None,
  "bank_slip": {
    "digitable_line": "00000000000000000000000000000000000000000000000",
    "barcode_data": "00000000000000000000000000000000000000000000",
    "barcode": "http://iugu.com/invoices/barcode/0958d2aa-d340-49ab-8895-83e26dfa0bf1-2f4c"
  },
  "items": [
    {
      "id": "11DA8B1662EC4C30BC4C78AEDC619145",
      "description": "Item Um",
      "price_cents": 1000,
      "quantity": 1,
      "created_at": "2014-06-17T09:58:05-03:00",
      "updated_at": "2014-06-17T09:58:05-03:00",
      "price": "R$ 10,00"
    }
  ],
  "variables": [
    {
      "id": "A897DD8BB6B54AE18CA4C48684E72FB9",
      "variable": "payment_data.transaction_number",
      "value": "1111"
    }
  ],
  "custom_variables": [],
  "logs": [],
  "credit_card_transaction": {
    "status": "authorized",
    "message": "Autorizado",
    "success": True,
    "lr": "00",
    "reversible": False,
    "token": "A897DD8BB6B54AE18CA4C48684E72FB9",
    "brand": "master",
    "bin": "409876",
    "last4": "1234",
    "created_at": "2014-06-17T09:58:05-03:00",
    "updated_at": "2014-06-17T09:58:05-03:00",
    "authorized_at": "2014-06-17T09:58:05-03:00",
    "captured_at": "2014-06-17T09:58:05-03:00",
    "canceled_at": "2014-06-17T09:58:05-03:00"
  }
}
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
