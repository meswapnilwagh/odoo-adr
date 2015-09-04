# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('requested','Requested'),
        ('confirmed', 'Esperando Aprobacion CC'),
        ('pre_confirmed','Esperando Auditoria'),
        ('post_confirmed','Esperando Auditoria'),
        ('audited','Esperando Autorizacion Dir. Financiera'),
        ('authorized','Esperando Confirmacion Dir. Ejecutiva'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'audited': [('readonly', True)],
        'authorized': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)]
    }

    _track = {
        'state': {
            'purchase.mt_rfq_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirmed',
            'purchase.mt_rfq_approved': lambda self, cr, uid, obj, ctx=None: obj.state == 'approved',
            'purchase.mt_rfq_done': lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
            'purchase.mt_rfq_audited': lambda self, cr, uid, obj, ctx=None: obj.state == 'audited',
            'purchase.mt_rfq_authorized': lambda self, cr, uid, obj, ctx=None: obj.state == 'authorized',
        },
    }
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
                                  help="The status of the purchase order or the quotation request. "
                                       "A request for quotation is a purchase order in a 'Draft' status. "
                                       "Then the order has to be confirmed by the user, the status switch "
                                       "to 'Confirmed'. Then the supplier must confirm the order to change "
                                       "the status to 'Approved'. When the purchase order is paid and "
                                       "received, the status becomes 'Done'. If a cancel action occurs in "
                                       "the invoice or in the receipt of goods, the status becomes "
                                       "in exception.",
                                  select=True, copy=False),
        'requester' : fields.many2one('res.users', 'Requested by', readonly=True, copy=False),
        'auditor' : fields.many2one('res.users', 'Audited by', readonly=True, copy=False),
        'authorizer' : fields.many2one('res.users', 'Authorized by', readonly=True, copy=False),
        #'validator' : fields.many2one('res.users', 'Validated by', readonly=True, copy=False),
        }

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not any(line.state != 'cancel' for line in po.order_line):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'requester' : uid})
        return True

    def wkf_pre_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not any(line.state != 'cancel' for line in po.order_line):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'pre_confirmed', 'requester' : uid})
        return True

    def action_audit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'audited', 'auditor' : uid}, context=context)
        return True

    def action_authorize(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'authorized', 'authorizer' : uid}, context=context)
        return True

class purchase_config_settings(osv.osv_memory):
    _inherit = 'purchase.config.settings'
    _columns = {
        'limit_amount': fields.integer('limit to require a second approval',required=True,
            help="Amount after which validation of purchase is required."),
    }

    _defaults = {
        'limit_amount': 5000,
    }

    def get_default_limit_amount(self, cr, uid, fields, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        transition = ir_model_data.get_object(cr, uid, 'purchase_custom_validation', 'trans_draft_pre_confirmed')
        field, value = transition.condition.split('<', 1)
        return {'limit_amount': int(value)}

    def set_limit_amount(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        config = self.browse(cr, uid, ids[0], context)
        waiting = ir_model_data.get_object(cr, uid, 'purchase_custom_validation', 'trans_draft_confirmed')
        waiting.write({'condition': 'amount_total >= %s' % config.limit_amount})
        approve = ir_model_data.get_object(cr, uid, 'purchase_custom_validation', 'trans_confirmed_approve')
        approve.write({'condition': 'amount_total >= %s' % config.limit_amount})
        confirm = ir_model_data.get_object(cr, uid, 'purchase_custom_validation', 'trans_draft_pre_confirmed')
        confirm.write({'condition': 'amount_total < %s' % config.limit_amount})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
