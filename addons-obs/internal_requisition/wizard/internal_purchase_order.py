# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd(<http://www.cozybizs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time
from openerp import models, fields, api, _ 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class internal_purchase_order(models.TransientModel):
    _name = 'internal.purchase.order'
    _description = 'Internal Purchase Order'
 
    
    def _compute_stock_loc(self):
        ir = self.env.context.get('active_id', False)
        ir_obj = self.env['internal.requisition']
        req = ir_obj.browse(ir)
        if req.warehouse_id:
            return req.warehouse_id.lot_stock_id.id
        return False
        
    def _compute_suppliers(self):
        ir = self.env.context.get('active_id', False)
        ir_obj = self.env['internal.requisition']
        ir_line_obj = self.env['internal.requisition.line']
        req = ir_obj.browse(ir)
        suppliers = []
        for line in req.line_ids:
            for supplier in line.product_id.seller_ids:
                suppliers.append(supplier.name.id)
        return [(6,0,suppliers)]
        
    supplier_ids = fields.Many2many('res.partner', 'ir_po_supp_rel', 'ir_po_id', 'supplier_id', 'Suppliers', default=_compute_suppliers, required=True)
    location_id = fields.Many2one('stock.location', 'Destination Location',default=_compute_stock_loc, help='This is the location where the incoming items will be received  (i.e the stock location)', required=True)
        
    @api.model
    def test_lines_po_state(self, ir):
        if ir:
            for line in ir.line_ids:
                if line.state in ('assigned', 'done', 'cancel'):
                    continue
                if not line.po_created:
                    return False
        return True
    
    @api.multi
    def request_rfq(self):
        self.create_all()
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def create_all(self):
        ir = self.env.context.get('active_id', False)
        ir_obj = self.env['internal.requisition']
        po_obj = self.env['purchase.order']
        purchase_order = False
        
        for rec in self:
            req = ir_obj.browse(ir)
            if req.po_created:
                raise Warning(_('Error !'), _('Purchase Order is already generated for this request !'))
            else:
                #analytic_ids = self.env['account.analytic.account'].search([('department_id', '=', req.department_id.id)])
                if req.delivery_ids:
                    po_lines = {}
                    for supp in rec.supplier_ids:
                        po_lines[supp] = []
                        for do in req.delivery_ids:
                            if do.state != 'done':
                                for line in do.move_lines:
                                    if line.state == 'confirmed':
                                        vals = {}
                                        if not(line.state in ('assigned', 'done', 'cancel')):
                                            vals = {
                                                'name': line.product_id.partner_ref,
                                                'product_id': line.product_id.id,
                                                'product_qty': line.product_uom_qty,
                                                'product_uom': line.product_uom.id,
                                                'price_unit': line.price_unit,
                                                'date_planned': line.date_expected,
                                                'company_id': line.company_id.id,
                                                #'account_analytic_id': analytic_ids and analytic_ids[0] or False,
                                            }
                                            po_lines[supp].append((0, 0, vals))

                for supp, val in po_lines.iteritems():
                    if len(val):
                        vals = {
                            'name': self.env['ir.sequence'].get('purchase.order'),
                            'partner_id': supp.id,
                            'origin': req.name,
                            'location_id': rec.location_id.id,
                            'pricelist_id': supp.property_product_pricelist_purchase.id,
                            'order_line': val,
                            'internal_requisition_id': req.id
                        }
                        purchase_order = po_obj.create(vals)
                if purchase_order:
                    req.write({'po_created': True})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: