
from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import UserError
from werkzeug import urls

_logger = logging.getLogger(__name__)
odoo_request = request

try:
    import iugu
except ImportError:
    _logger.warning("Não é possível importar iugu", exc_info=True)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    invoice_url = fields.Char(string="Fatura IUGU", size=300)

    @api.model
    def _iugu_form_get_tx_from_data(self, data):
        acquirer_reference = data.get("data[id]")
        tx = self.search([("acquirer_reference", "=", acquirer_reference)])
        return tx[0]

    def _iugu_form_validate(self, data):
        status = data.get("data[status]")

        if status in ('paid', 'partially_paid', 'authorized'):
            self._set_transaction_done()
            return True
        elif status == 'pending':
            self._set_transaction_pending()
            return True
        else:
            self._set_transaction_cancel()
            return False