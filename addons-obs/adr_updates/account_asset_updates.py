# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
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
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
import pdb
import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression, orm
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.exceptions import except_orm, Warning, RedirectWarning

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class ProductTemplate(osv.osv):
    _inherit = "product.template"

    _columns = {
        'fixed_asset': fields.boolean(string="Es Activo Fijo"),
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category',
                                             domain=[('type','=','normal')]),
    }

class AssetAsset(osv.osv):
    _inherit = "asset.asset"

    _defaults = {
        'asset_number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'asset.asset.number')
    }

class AccountAssetCategory(osv.osv):
    _order = "parent_left"
    _name = 'account.asset.category'
    _inherit = 'account.asset.category'

    def _get_children(self, cr, uid, ids, context=None):

        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        if ids3:
            ids3 = self._get_children(cr, uid, ids3, context)
        return ids2 + ids3

    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []
        return result

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            level = 0
            parent = category.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[category.id] = level
        return res

    _columns = {
        'type': fields.selection(string="Tipo Interno", selection=[('view', 'View'),
                                                                   ('normal', 'Normal'), ], required=True),
        'parent_id': fields.many2one("account.asset.category", string="Categoria Padre",
                                     required=False, ondelete='cascade', domain=[('type','=','view')]),
        'child_parent_ids': fields.one2many("account.asset.category", "parent_id", string="Hijos", required=False, ),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="account.asset.category",
                                    string="Categoria(s) Hijas"),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'level': fields.function(_get_level, string='Nivel', method=True, type='integer',
                                 store={'account.asset.category': (_get_children, ['level', 'parent_id'], 10), }),

    }

    _defaults = {
        'type': 'normal',
    }


class account_asset(osv.osv):
    _inherit = 'account.asset.asset'

    def onchange_asset_category(self,cr, uid, ids, category_id, context=None):
        account_asset_cat_obj = self.pool.get('account.asset.category')
        parent_id = False
        if category_id:
            category_id_rec = account_asset_cat_obj.browse(cr, uid, category_id, context)
            parent_id = category_id_rec.parent_id.id
            self.write(cr, uid, ids, {
                'category_parent_id': parent_id
            })
        return {'value': {'category_parent_id': parent_id}}

    def get_period(self, cr, uid, id, context=None):
        """Retrieves the period corresponding to the passed depreciation
        line and returns its id."""
        period_obj = self.pool.get('account.period')
        depreciation_obj = self.pool.get('account.asset.depreciation.line')
        depre_date = depreciation_obj.browse(cr, uid, id,
                                             context).depreciation_date.split('-')
        period_id = period_obj.search(cr, uid,
                                      [('code', '=', '{0}/{1}'.format(depre_date[1], depre_date[0]))],
                                      limit=1)
        try:
            return period_id[0]
        except IndexError, e:
            return False

    def prepare_account_move(self, cr, uid, depreciation_line_id, period_id, context=None):
        """Setup values to create a new account move based in asset depreciation line

        Args:
            depreciation_line_id; int
            period_id; int

        Return:
            dictionary
            """
        asset_line_obj = self.pool.get('account.asset.depreciation.line')
        asset_line = asset_line_obj.browse(cr, uid, depreciation_line_id, context)
        asset_name = asset_line.name.encode('utf-8')
        res = {
            'name': asset_name,
            'period_id': period_id,
            'state': 'draft',
            'ref': asset_name,
            'date': date.today().isoformat(),
            'journal_id': asset_line.asset_id.category_id.journal_id.id,
            'company_id': asset_line.asset_id.company_id.id
        }
        return res

    def prepare_move_line(self, cr, uid, line_id, move_id, period_id,
                          move_type, context=None):
        """Returns the values to create an account move line.

        Args:
            line_id; depreciation line id
            move_id; parent account.move id
            type; string; debit or credit

        Returns:
            {field: value}
        """
        line_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        line = line_obj.browse(cr, uid, line_id, context)
        company_currency = line.asset_id.company_id.currency_id.id
        asset_currency = line.asset_id.currency_id.id
        amount = currency_obj.compute(cr, uid, asset_currency, company_currency,
                                      line.amount, context)
        sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
        amount_currency = (company_currency != asset_currency and - sign *
                           line.amount or 0.0)
        if move_type == 'debit':
            debit, credit = amount, 0.0
            account = line.asset_id.category_id.account_depreciation_id.id
            asset = None
        else:
            debit, credit = 0.0, amount
            account = line.asset_id.category_id.account_expense_depreciation_id.id
            asset = line.asset_id.id
        values = {
            'name': line.asset_id.name.encode('utf-8'),
            'partner_id': line.asset_id.partner_id.id,
            #LOV Python
            'debit': debit and credit or credit,
            'credit': debit and credit or debit,
            'move_id': move_id,
            'ref': line.name.encode('utf-8'),
            'account_id': account,
            'journal_id': line.asset_id.category_id.journal_id.id,
            'currency_id': company_currency != asset_currency and asset_currency or False,
            'date': date.today().isoformat(),
            'amount_currency': amount_currency,
            'period_id': period_id,
            'asset_id': asset,
            'company_id': line.asset_id.company_id.id,
        }
        return values

    def get_asset_ids(self, cr, context=None):
        """Retrieve the assets using SQL for a better performance."""
        query = """SELECT id from {0} WHERE active = True and state like 'open'"""
        query = query.format(self._table)
        cr.execute(query)
        ids = [asset[0] for asset in cr.fetchall() if asset]
        return ids

    def run_asset_entry(self, cr, uid, context=None):
        """Method that checks all lines in the model account asset
        deprecated and if the date is equal or greater than today it
        creates the account entry with the status settled.

        Args:
            cr, uid, ids, context

        Return:
            List of created account moves
        """

        logging.getLogger(self._name).info("Starting run_asset_entry cron job.")
        account_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        asset_lines_obj = self.pool.get('account.asset.depreciation.line')
        ids = self.get_asset_ids(cr)
        for asset in ids:
            asset = self.read(cr, uid, asset, context=context)
            for asset_line in asset.get('depreciation_line_ids'):
                today = date.today()
                asset_name = asset.get('name').encode('utf-8')
                asset_line = asset_lines_obj.read(cr, uid, asset_line, context)

                if asset_line.get('depreciation_date') <= today.isoformat() and not asset_line.get('move_check'):
                    period_id = self.get_period(cr, uid, asset_line.get('id'))

                    if not period_id:
                        company_name = asset.get('company_id')
                        logging.getLogger(self._name).error(
                            """No period found for the date {0}
                            and company {1}""".format(asset_line.get('depreciation_date'), company_name[1]))
                        break
                    try:
                        values = self.prepare_account_move(cr, uid,
                                                           asset_line.get('id'),
                                                           period_id, context)
                        created_id = account_move_obj.create(cr, uid, values,
                                                             context)
                        logging.getLogger(self._name).info("""account.move created for {0}""".format(asset_name))
                    except:
                        logging.getLogger(self._name).error("Error creating account move {0}".format(asset_name))
                        raise orm.except_orm('Error', "Failure creating the account move object.")
                    try:
                        debit_values = self.prepare_move_line(cr, uid,
                                                              asset_line.get('id'),
                                                              created_id,
                                                              period_id,
                                                              'debit')
                        credit_values = self.prepare_move_line(cr, uid,
                                                               asset_line.get('id'),
                                                               created_id,
                                                               period_id,
                                                               'credit')
                        move_line_obj.create(cr, uid, debit_values,
                                                        context)
                        move_line_obj.create(cr, uid, credit_values,
                                                         context)
                        asset_lines_obj.write(cr, uid, asset_line.get('id'),
                            {'move_check': True, 'move_id': created_id})
                        logging.getLogger(self._name).info("""account.move.line created for {0}""".format(asset_name))
                    except:
                        logging.getLogger('account.asset.asset').error(
                            """ERROR creating the entries of
                            account move from {0}.""".format(__name__))
                        raise orm.except_orm('Error', 'Failure creating the'
                            ' account move lines.')
                else:
                    logging.getLogger(self._name).info("Este activo ya esta asentado!")

    _columns = {
        'asset_code': fields.char('Codigo', size=32, required=False, readonly=False),
        'category_id': fields.many2one('account.asset.category', 'Asset Category', required=True,
                                       change_default=True, readonly=True, states={'draft':[('readonly',False)]},
                                       domain=[('type','=','normal')]),
        'category_parent_id': fields.many2one("account.asset.category", string="Categoria Padre del Activo",
                                              required=False, readonly=True, states={'draft':[('readonly',False)]},
                                              domain=[('type','=','view')] ),
        'account_analytic_id': fields.many2one("account.analytic.account", string="Cuenta analitica",
                                               required=True, domain=[('type','=','normal')]),
        'asset_move_ids': fields.one2many('account.asset.move', 'asset_id','Movimientos'),

        #'asset_move_ids': fields.one2many('account.asset.move', 'asset_id', 'Movements')
    }

    _defaults = {
        'asset_code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'asset.number')
    }


class AssetMove(orm.Model):

    _name = 'account.asset.move'
    _description = 'Movimiento de Activo Fijo'

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'audited': [('readonly', True)],
        'received': [('readonly', True)],
        'validated': [('readonly', True)]
    }

    _columns = {
        'asset_id': fields.many2one('account.asset.asset', 'Activo', required=True,
                                    domain=[('state','not in',['draft','close'])], states=READONLY_STATES,),
        'asset_code': fields.related('asset_id', 'asset_code', string='Codigo', readonly=True, type="char"),
        'partner_id': fields.many2one('res.partner', 'Empleado / Cliente', states=READONLY_STATES,),
        'origin_company': fields.many2one('res.company', 'Filial Origen', states=READONLY_STATES,),
        'origin_account_analytic_id': fields.many2one('account.analytic.account', 'Departamento Origen',
                                                      states=READONLY_STATES,),
        'destiny_company': fields.many2one('res.company', 'Filial Destino', states=READONLY_STATES,),
        'destiny_account_analytic_id': fields.many2one('account.analytic.account', 'Departamento Destino',
                                                       domain=[('type','=','normal')], states=READONLY_STATES,),
        'date': fields.date('Fecha', require=True, help="""Fecha cuando se ejecutara el movimiento""",
                            states=READONLY_STATES,),
        'movement_category': fields.selection((('company_change', 'Cambio de Empresa'),
                                               ('department_change', 'Cambio de Departamento'),
                                               ('donation_employee', 'Donacion - Empleados'),
                                               ('donation_patient', 'Donacion - Pacientes'),
                                               ('lent', 'Lent')), 'Tipo de movimiento',
                                              required=True, help="""The category to wich the movement belongs.""",
                                              states=READONLY_STATES,),
        'state': fields.selection((('draft', 'Borrador - Esperando confirmacion director departamento'),
            ('confirmed', 'Confirmado - Esperando Auditoria'),
            ('audited', 'Auditado - Esperando recepcion'),
            ('received', 'Recibido - Esperando validacion'),
            ('validated', 'Validado'),
            ('cancel', 'Cancel')), 'Status', required=True),
        'notes': fields.char('Notas', states=READONLY_STATES,),
        'requester': fields.many2one('res.users', 'Solicitador por:', readonly=True),
        'confirmer': fields.many2one('res.users', 'Confirmado por:', readonly=True),
        'auditor': fields.many2one('res.users', 'Auditado por:', readonly=True),
        'receiver': fields.many2one('res.users', 'Recibido por:', readonly=True),
        'validator': fields.many2one('res.users', 'Validado por:', readonly=True),
        'canceler': fields.many2one('res.users', 'Cancelado por:', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'date': fields.datetime.now,
        'requester': lambda obj, cr, uid, context: uid,
    }

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed', 'confirmer': uid})
        return True

    def action_audit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'audited', 'auditor': uid})
        return True

    def action_receive(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'received', 'receiver': uid})
        return True

    def action_validate(self, cr, uid, ids, context=None):
        obj_self = self.browse(cr, uid, ids[0], context=context)
        movement_cat = obj_self.movement_category

        asset_id = obj_self.asset_id.id
        account_asset_obj = self.pool.get('account.asset.asset')

        #if movement_cat == 'company_change' or movement_cat == 'department_change':
        if movement_cat in ['company_change', 'department_change']:

            destiny_company = obj_self.destiny_company.id or obj_self.origin_company.id
            destiny_account_analytic_id = obj_self.destiny_account_analytic_id.id or obj_self.origin_account_analytic_id.id

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                vals = {'company_id': destiny_company,
                        'account_analytic_id': destiny_account_analytic_id,
                        }
                asset = account_asset_obj.write(cr, uid, asset_id, vals, context=context)

        elif movement_cat in ['donation_employee','donation_patient']:
            pdb.set_trace()
            context = dict(context or {})
            can_close = False
            asset_obj = self.pool.get('account.asset.asset')
            asset_lines_obj = self.pool.get('account.asset.depreciation.line')
            period_obj = self.pool.get('account.period')
            move_obj = self.pool.get('account.move')
            move_line_obj = self.pool.get('account.move.line')
            currency_obj = self.pool.get('res.currency')
            created_move_ids = []
            asset_ids = []
            '''
            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                asset = account_asset_obj.read(cr, uid, asset_id, context=context)


                for asset_line in asset.get('depreciation_line_ids'):
                    if asset_line.get('move_check'):
                        depreciation_amount += asset_line.amount
            '''
            depreciation_amount = 0.00

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                move_checks = asset_lines_obj.search(cr, uid, [("asset_id", "=", asset_id), ("move_check", "=", True)])
                for move_checks_lines in asset_lines_obj.browse(cr, uid, move_checks):
                    depreciation_amount += move_checks_lines.amount

                depreciation_date = time.strftime('%Y-%m-%d')
                period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                #context.update({'date': depreciation_date})
                purchase_value = currency_obj.compute(cr, uid, current_currency, company_currency,
                                                      asset.purchase_value, context=context)
                sign = (asset.category_id.journal_id.type == 'purchase' and 1) or -1
                asset_name = asset.name
                reference = asset.name
                residual_value = abs(purchase_value-depreciation_amount)
                move_vals = {
                    'name': asset_name,
                    'date': depreciation_date,
                    'ref': reference,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': asset.category_id.journal_id.id,
                    }
                move_id = move_obj.create(cr, uid, move_vals, context=context)
                journal_id = asset.category_id.journal_id.id
                partner_id = asset.partner_id.id
                #Linea de asiento contable: Credito a Cuenta de Activo por el costo de adquisicion del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_asset_id.id,
                    'debit': 0.0,
                    'credit': purchase_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and - sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })
                #Linea de asiento contable: Debito a cuenta de amortizacion por el valor de la depreciacion acumulada

                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_depreciation_id.id,
                    'credit': 0.0,
                    'debit': depreciation_amount,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })
                #Linea de asiento contable: Debito a cuenta de gasto de amortizacion  por el valor residual del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_expense_depreciation_id.id,
                    'credit': 0.0,
                    'debit': residual_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,
                    'asset_id': asset.id
                })
                self.write(cr, uid, asset.id, {'move_id': move_id}, context=context)
                created_move_ids.append(move_id)
                asset_ids.append(asset.id)
            # we re-evaluate the assets to determine whether we can close them
            for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
                if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                    asset.write({'state': 'close'})

            account_asset_obj.write(cr, uid, asset_id, {'state': 'close'}, context=context)

#            return created_move_ids
        self.write(cr, uid, ids, {'state': 'validated', 'validator': uid})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel',
                                  'confirmer': False,
                                  'auditor': False,
                                  'receiver': False,
                                  'validator': False})

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft',
                                  'confirmer': False,
                                  'auditor': False,
                                  'receiver': False,
                                  'validator': False})
        return True


    def onchange_asset(self, cr, uid, ids, asset_id, context=None):
        """On change method for the asset. Gets the department and company of
        origin of the asset."""
        account_asset_obj = self.pool.get('account.asset.asset')
        company_id = False
        account_analytic_id = False

        if asset_id:
            asset_rec = account_asset_obj.browse(cr, uid, asset_id, context)
            company_id = asset_rec.company_id.id
            account_analytic_id = asset_rec.account_analytic_id.id

            self.write(cr, uid, ids, {
                'origin_company': company_id,
                'origin_account_analytic_id': account_analytic_id})
        return {'value': {'origin_company': company_id,
                               'origin_account_analytic_id': account_analytic_id}}

    @api.multi
    def unlink(self):
        for move in self:
            if move.state not in ('draft', 'cancel'):
                raise Warning(_('No puede eliminar un movimiento que no este en borrador o cancelado.'))
            #elif invoice.internal_number:
            #    raise Warning(_('You cannot delete an invoice after it has been validated (and received a number).
            # You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        return super(AssetMove, self).unlink()

AssetMove()
