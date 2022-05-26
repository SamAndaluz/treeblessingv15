# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PagseguroController(http.Controller):
    _accept_url = '/payment/pagseguro/feedback'

    @http.route(_accept_url, type='http', auth='public', methods=['POST'], csrf=False)
    def pagseguro_form_feedback(self, **post):
        _logger.info("beginning _handle_feedback_data with post data %s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('pagseguro', post)
        return request.redirect('/payment/status')
