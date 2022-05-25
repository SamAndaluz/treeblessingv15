
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError
from werkzeug import urls
import pprint
import logging
import datetime
import re

_logger = logging.getLogger(__name__)
odoo_request = request

try:
    import iugu
except ImportError:
    _logger.warning("Não é possível importar iugu", exc_info=True)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    invoice_url = fields.Char(string="Fatura IUGU", size=300)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Iugu-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific rendering values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'iugu':
            return res

        payload = self._iugu_prepare_payment_request_payload()
        _logger.info("sending '/payments' request for link creation:\n%s", pprint.pformat(payload))
        payment_data = self.acquirer_id._iugu_make_request(data=payload)

        # The acquirer reference is set now to allow fetching the payment status after redirection
        self.write({'acquirer_reference':payment_data.get('id'),
                    'invoice_url':payment_data.get("secure_url")})

        return {'api_url': payment_data.get("secure_url")}

    def _iugu_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        base_url = (self.env["ir.config_parameter"].sudo().get_param("web.base.url"))

        partner_id = self.partner_id

        items = [{
            "description": 'Fatura Ref: %s' % self.reference,
            "quantity": 1,
            "price_cents": int(self.amount * 100),
        }]

        today = datetime.date.today()

        invoice_data = {
            "email": partner_id.email,
            "due_date": today.strftime("%d/%m/%Y"),
            "return_url": urls.url_join(base_url, "/payment/status"),
            "notification_url": urls.url_join(base_url, "/iugu/notificacao/"),
            "items": items,
            "payer": {
                "name": partner_id.name,
                #"cpf_cnpj": partner_id.cnpj_cpf,
                "address": {
                    "street": partner_id.street,
                    "city": partner_id.city,
                    #"number": partner_id.number,
                    "zip_code": re.sub('[^0-9]', '', partner_id.zip or ''),
                },
            },
        }
        return invoice_data


    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Iugu data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'iugu':
            return tx

        tx = self.search([('reference', '=', data.get('ref')), ('provider', '=', 'iugu')])
        if not tx:
            raise ValidationError(
                "iugu: " + _("No transaction found matching reference %s.", data.get('ref'))
            )
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Iugu data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'iugu':
            return

        payment_data = self.acquirer_id._iugu_make_request(invoice_id =self.acquirer_reference, method="GET")
        payment_status = payment_data.get('status')

        if payment_status == 'pending':
            self._set_pending()
        elif payment_status == 'authorized':
            self._set_authorized()
        elif payment_status == 'paid':
            self._set_done()
        elif payment_status in [ 'canceled', 'failed']:
            self._set_canceled("iugu: " + _("Canceled payment with status: %s", payment_status))
        else:
            _logger.info("Received data with invalid payment status: %s", payment_status)
            self._set_error(
                "iugu: " + _("Received data with invalid payment status: %s", payment_status)
            )
