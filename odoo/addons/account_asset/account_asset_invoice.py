# -*- encoding: utf-8 -*-
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
import pdb

class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, *args):
        result = super(account_invoice, self).action_number(cr, uid, ids, *args)
        for inv in self.browse(cr, uid, ids):
            self.pool.get('account.invoice.line').asset_create(cr, uid, inv.invoice_line)
        return result

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res['asset_id'] = x.get('asset_id', False)
        return res


class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'

    _columns = {
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
    }

    def asset_create(self, cr, uid, lines, context=None):

        context = context or {}

        product_obj = self.pool.get('product.template')
        asset_obj = self.pool.get('account.asset.asset')
        asset_asset_obj = self.pool.get('asset.asset')
        for line in lines:
            pdb.set_trace()
            qty = str(line.quantity)
            for each in qty:

                if line.asset_category_id:
                    asset_asset_vals = {
                        'name': line.name,
                        'vendor_id': line.partner_id.id,
                        #'purchase_date': line.invoice_id.date_invoice,
                    }
                    vals = {
                        'name': line.name,
                        'code': line.invoice_id.number or False,
                        'asset_id': asset_asset_obj.create(cr, uid, asset_asset_vals, context=context),
                        'category_id': line.asset_category_id.id,
                        'category_parent_id': line.asset_category_id.parent_id.id or False,
                        'account_analytic_id': line.account_analytic_id.id or False,
                        'purchase_value': line.price_unit,
                        'period_id': line.invoice_id.period_id.id,
                        'partner_id': line.invoice_id.partner_id.id,
                        'company_id': line.invoice_id.company_id.id,
                        'currency_id': line.invoice_id.currency_id.id,
                        'purchase_date': line.invoice_id.date_invoice,
                    }

                    changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
                    vals.update(changed_vals['value'])
                    asset_id = asset_obj.create(cr, uid, vals, context=context)

                    if line.asset_category_id.open_asset:
                        asset_obj.validate(cr, uid, [asset_id], context=context)

                    product_id = line.product_id
                    if not product_id.fixed_asset:
                        vals = {'fixed_asset': True,
                                'asset_category_id': line.asset_category_id.id}

                        product = product_obj.write(cr, uid, product_id.id, vals, context=context)

        return True




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
