import pprint
import logging
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IuguController(http.Controller):
    _notify_url = '/iugu/notificacao/'

    @http.route(_notify_url, type='http', auth='public', methods=['POST'], csrf=False)
    def iugu_notify(self, **data):
        """ Process the data sent by Iugu to the webhook.

        :param dict data: The feedback data (only `id`) and the transaction reference (`ref`)
                          embedded in the return URL
        :return: An empty string to acknowledge the notification
        :rtype: str
        """
        _logger.info("Received iugu notify data:\n%s", pprint.pformat(data))
        try:
            request.env['payment.transaction'].sudo()._handle_feedback_data('iugu', data)
        except ValidationError:  # Acknowledge the notification to avoid getting spammed
            _logger.exception("unable to handle the notification data; skipping to acknowledge")
        return ''  # Acknowledge the notification with an HTTP 200 response

    @http.route(
        '/iugu/checkout/redirect', type='http', auth='none', methods=['GET', 'POST'])
    def iugu_checkout_redirect(self, **post):
        post = post
        if 'secure_url' in post:
            return redirect(post['secure_url'])
