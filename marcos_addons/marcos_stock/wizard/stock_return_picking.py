# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'

    _columns = {
        'afecta': fields.char("Factura que afecta", size=19, readonly=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)

        picking_id = self.pool.get("stock.picking").browse(cr, uid, context["active_id"], context=context)
        if picking_id.invoice_id or picking_id.group_id:
            if picking_id.invoice_id.number:
                res.update({"afecta": picking_id.invoice_id.number, "invoice_state": "2binvoiced"})
            # else:
            #     raise osv.except_osv(u'No puede hacer esta devolución!', u"El pedido de compra relacionado a este conduce no esta facturado!")

        return res

    def _create_returns(self, cr, uid, ids, context=None):
        context = context or {}
        res = super(stock_return_picking, self)._create_returns(cr, uid, ids, context=context)
        data = self.browse(cr, uid, ids[0], context=context)

        if data.afecta:
            afecta_invoice_id = self.pool.get("account.invoice").search(cr, uid, [('number', '=', data.afecta)])
            new_picking = self.pool.get("stock.picking").write(cr, uid, res[0],
                                                               {"afecta": afecta_invoice_id[0],
                                                                "invoice_id": False}, context=context)

        return res

