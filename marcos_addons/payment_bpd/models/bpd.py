# -*- coding: utf-8 -*-
# #############################################################################
#
# Copyright (c) 2014 Marcos Organizador de Negocios- Eneldo Serrata - http://marcos.do
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company like Marcos Organizador de Negocios.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# #############################################################################

try:
    import simplejson as json
except ImportError:
    import json
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.osv import osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _
import urlparse
import urllib2
import logging
import pprint

_logger = logging.getLogger(__name__)

from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
from openerp.tools import float_round

_logger = logging.getLogger(__name__)


class TransferPaymentAcquirer(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_providers(self, cr, uid, context=None):
        providers = super(TransferPaymentAcquirer, self)._get_providers(cr, uid, context=context)
        providers.append(['bpd', 'Banco Popular'])
        return providers

    def _get_bpd_urls(self, cr, uid, acquirer, context=None):
        if acquirer.environment == 'prod':
            return {
                'bpd_form_url': acquirer.bpd_url_prod
            }
        else:
            return {
                'bpd_form_url': acquirer.bpd_url_test
            }

    def bpd_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/transfer/bpd'

    _columns = {
        'bpd_url_test': fields.char("BPD Url service de prueba", required=True),
        'bpd_url_prod': fields.char("BPD Url service", required=True),
        'bpd_auth1_test': fields.char('Auth1 de prueba', required=True),
        'bpd_auth1_prod': fields.char('Auth1', required=True),
        'bpd_auth2_test': fields.char('Auth2 de prueba', required=True),
        'bpd_auth2_prod': fields.char('Auth2', required=True),
        'bpd_channel_test': fields.char('Channel de prueba', size=3, required=True,
                                        help=u"""Identifica el canal por el cual se está recibiendo: ECO = Ecommerce"""),
        'bpd_channel_prod': fields.char('Channel', size=3, required=True,
                                        help=u"""Identifica el canal por el cual se está recibiendo: ECO = Ecommerce"""),
        'bpd_store_test': fields.char('Store de prueba', size=11, required=True,
                                      help=u"Identificador del sitio originador de la transacción"),
        'bpd_store_prod': fields.char('Store', size=11, required=True,
                                      help=u"Identificador del sitio originador de la transacción"),
        'bpd_posinputmode_test': fields.char('PosInputMode de prueba', size=10, required=True,
                                             help=u"""Modo de Ingreso: E-Commerce = Comercio electrónico."""),
        'bpd_posinputmode_prod': fields.char('PosInputMode', size=10, required=True,
                                             help=u"""Modo de Ingreso: E-Commerce = Comercio electrónico."""),
        'service_phone': fields.char(u"Número de servicio para atención telefónica", size=10),
        'ecommerceurl': fields.char("E-Commerce URL", size=32)
    }

    _defaults = {
        'bpd_url_test': 'false',
        'bpd_auth1_test': 'false',
        'bpd_auth2_test': 'false',
        'bpd_channel_test': 'EC',
        'bpd_store_test': 'false',
        'bpd_posinputmode_test': 'E-Commerce',
        'bpd_url_prod': 'false',
        'bpd_auth1_prod': 'false',
        'bpd_auth2_prod': 'false',
        'bpd_channel_prod': 'EC',
        'bpd_store_prod': 'false',
        'bpd_posinputmode_prod': 'E-Commerce'
    }


class TransferPaymentTransaction(osv.Model):
    _inherit = 'payment.transaction'

    def _bpd_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx_ids = self.search(cr, uid, [('reference', '=', reference)], context=context)

        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return self.browse(cr, uid, tx_ids[0], context=context)

    def _bpd_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        if float_compare(float(data.get('amount', '0.0')), tx.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % tx.amount))
        if data.get('currency') != tx.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), tx.currency_id.name))

        tx_bpd_request = {}
        if tx.acquirer_id.environment == 'prod':
            tx_bpd_request.update({
                "Channel": tx.acquirer_id.bpd_channel_prod,
                "Store": tx.acquirer_id.bpd_store_prod,
                "PosInputMode": tx.acquirer_id.bpd_posinputmode_prod
            })
            tx_url = tx.acquirer_id.bpd_url_prod
            Auth1 = tx.acquirer_id.bpd_auth1_prod
            Auth2 = tx.acquirer_id.bpd_auth2_prod
        else:
            tx_bpd_request.update({
                "Channel": tx.acquirer_id.bpd_channel_test,
                "Store": tx.acquirer_id.bpd_store_test,
                "PosInputMode": tx.acquirer_id.bpd_posinputmode_test
            })
            tx_url = tx.acquirer_id.bpd_url_test
            Auth1 = tx.acquirer_id.bpd_auth1_test
            Auth2 = tx.acquirer_id.bpd_auth2_test
            # cc_month, cc_year = data.get("cc_expiry").replace(" ", "").split("/")
        tx_bpd_request.update({
            # "CardNumber": u"4012000077777777",
            "CardNumber": int(data.get("cc_number").replace(" ", "")),
            "Expiration": 201701,#int("20%s%s" % (cc_year, cc_month)),
            "CVC": 201,#int(data.get("cc_cvc")),
            "TrxType": "Sale",
            "Amount": 100,#'%d' % int(float_round(float(data['amount']), 2) * 100),
            "CurrencyPosCode": "$" if data.get("currency") == u"DOP" else u"U$S",
            "Payments": "1",
            "Plan": "0",
            "AcquirerRefData": "1",
            "CustomerServicePhone": tx.acquirer_id.service_phone,
            "OrderNumber": data['reference'],
            "ECommerceUrl": tx.acquirer_id.ecommerceurl})

        request = urllib2.Request(tx_url, json.dumps(tx_bpd_request))
        request.add_header('Auth1', Auth1)
        request.add_header('Auth2', Auth2)
        request.add_header('Content-type', 'application/json')
        request = urllib2.urlopen(request)
        result = request.read()
        print result
        _logger.info('=========================BPD DEBUG RESPONSE BLOCK===========================')  # debug
        from pprint import pprint as pp

        _logger.info(pp(json.loads(result)))  # debug
        _logger.info('=========================BPD DEBUG RESPONSE BLOCK===========================')  # debug

        invalid_parameters.append(('cc_cvc', data.get('currency'), tx.currency_id.name))

        return invalid_parameters

    def _bpd_form_validate(self, cr, uid, tx, data, context=None):
        _logger.info('Validated transfer payment for tx %s: set as pending' % (tx.reference))
        return tx.write({'state': 'pending'})

    _columns = {
        'bpd_authorizationcode': fields.char(u'Código de autorización', size=10),
        'bpd_datetime': fields.char(u'Fecha y hora', size=10),
        'bpd_errordescription': fields.char(u'Descripción de error', size=10),
        'bpd_isocode': fields.char(u'Código de Respuesta', size=10),
        'bpd_lotnumber': fields.char(u'Número de lote', size=10),
        'bpd_rrn': fields.char(u'Número de referencia', size=10),
        'bpd_responsecode': fields.char(u'Código de respuesta', size=10),
        'bpd_responsemessage': fields.char(u'Mensaje de respuesta', size=10),
        'bpd_ticket': fields.char(u'Número de Ticket', size=10),
    }


import urllib2, httplib


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):

    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert


    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)


    def getConnection(self, host, timeout=300):

        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert, timeout=30000)

# opener = urllib2.build_opener(HTTPSClientAuthHandler('/path/to/file.pem', '/path/to/file.pem.'))
# response = opener.open("https://example.org")
#
# print response.read()




