
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)
odoo_request = request


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return pagseguro-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific rendering values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'pagseguro':
            return res

        pagseguro = self.acquirer_id._pagseguro_prepare_pagseguro_object()
        pagseguro = self._pagseguro_prepare_payment_request_payload(pagseguro)
        _logger.info("sending '/payments' request for link creation")
        response = pagseguro.checkout()
        _logger.info("Response Errors: %s" % (response.errors))

        # The acquirer reference is set now to allow fetching the payment status after redirection
        self.write({'acquirer_reference':response.reference})

        return {'api_url': response.payment_url}

    def _pagseguro_prepare_payment_request_payload(self, pg):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        pagseguro_tx_values = {}
        pagseguro_tx_values.update({
            'pagseguro_email': self.acquirer_id.pagseguro_email_account,
            'pagseguro_token': self.acquirer_id.pagseguro_token,
            'amount': format(self.amount, '.2f')
        })
        pg.reference_prefix = None
        pg.items = [
            {"id": "0001", "description": 'Fatura Ref: %s' % self.reference,
             "amount": pagseguro_tx_values['amount'], "quantity": 1},
        ]
        base_url = (self.env["ir.config_parameter"].sudo().get_param("web.base.url"))
        pg.redirect_url = base_url + pagseguro_tx_values.get('return_url', '/payment/status')
        _logger.info("Redirect Url: %s" % (pg.redirect_url))
        pg.notification_url = base_url + "/payment/pagseguro/feedback"
        return pg


    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on pagseguro data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'pagseguro':
            return tx

        tx = self.search([('reference', '=', data.get('ref')), ('provider', '=', 'pagseguro')])
        if not tx:
            raise ValidationError(
                "pagseguro: " + _("No transaction found matching reference %s.", data.get('ref'))
            )
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on pagseguro data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'pagseguro':
            return
        pagseguro = self.acquirer_id._pagseguro_prepare_pagseguro_object()
        notif = pagseguro.check_notification(data.get('notificationCode'))
        payment_status = notif.status
        if payment_status == 1:
            self._set_pending()
        elif payment_status == 3:
            self._set_done()
        elif payment_status in [ 'canceled', 'failed']:
            self._set_canceled("pagseguro: " + _("Canceled payment with status: %s", payment_status))
        else:
            _logger.info("Received data with invalid payment status: %s", payment_status)
            self._set_error(
                "pagseguro: " + _("Received data with invalid payment status: %s", payment_status)
            )
