#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the hr.payslip.run object.
#
#Author: José Ernesto Mendez @ Open Business Solutions
#
#
#####

from openerp.osv import orm, fields, osv

class hr_payslip_run (orm.Model) :

    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _columns = {
        'date_efective': fields.date('Fecha de Aplicacion', required=True,
            readonly=True, states={'draft':[('readonly', False)]}, select=True,
            help="""Date when the payment is applied. - The application date
            can't be lower than the date when the text file was sent to the
            bank."""),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency',
            required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'bank_id': fields.many2one('res.bank', 'Banco', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'sequence': fields.char('Payslip Batch Sequence', size=7,
            required=False, readonly=True, select=True, help="""Unique number
            of the payslip batch,computed automatically when the payslip batch
            is created."""),
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=True),
        'payroll_type': fields.selection([('fixed_employees', 'Empleados Fijos'),
                                          ('temporal_employees', 'Empleados Temporales'),
                                          ('probative_employees', 'Empleados Probatorios'),
                                          ('pensioner_employees', 'Pensionados'),
                                          ('commission_employees', 'Comisionistas')], 'Tipo de Nomina', required=True),
    }

    def _get_seq(self, cr, uid, ctx):

        seq = self.pool.get('ir.sequence').get(cr, uid, 'salary.slipbatch')
        return seq

    def _get_currency(self, cr, uid, ctx):

        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id

    def close_payslip_run(self, cr, uid, ids, context=None):
        slip_pool = self.pool.get('hr.payslip')
        slip_ids = [x.id for x in self.browse(cr, uid,ids[0], context=context).slip_ids]
        slip_pool.process_sheet(cr, uid, slip_ids, context=context)
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def confirm_payslips(self, cr, uid, ids, context=None):
        for payslip_run in self.browse(cr, uid, ids, context=context):
            payslip_obj = self.pool.get('hr.payslip')
            payslips = payslip_obj.browse(cr, uid, payslip_run.slip_ids, context)
            for payslip in payslips:
                payslip_id = payslip.id
                payslip_id.process_sheet()

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.payslip.run', context=c),
        'currency_id': _get_currency,
        'sequence': _get_seq,
    }

hr_payslip_run()

class hr_payslip(orm.Model):


    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    _columns = {
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=True),
        'payroll_type': fields.selection([('fixed_employees', 'Empleados Fijos'),
                                          ('temporal_employees', 'Empleados Temporales'),
                                          ('probative_employees', 'Empleados Probatorios'),
                                          ('pensioner_employees', 'Pensionados'),
                                          ('commission_employees', 'Comisionistas')], 'Tipo de Nomina', required=True),
        'pay_vacation': fields.boolean('Incluir Vacaciones'),
    }

hr_payslip()

class hr_salary_rule(orm.Model):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'

    _columns = {
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=False),
    }


class hr_payslip_employees(osv.osv_memory):
    _inherit = "hr.payslip.employees"
    #_logger = logging.getLogger(__name__)

    def compute_sheet(self, cr, uid, ids, context=None):
        #res = super(hr_payslip_employees, self).compute_sheet(
        #    cr, uid, ids, context)

        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(
                cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note', 'payment_period', 'payroll_type',])
        from_date = run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        payment_period = run_data.get('payment_period', False)
        payroll_type = run_data.get('payroll_type', False)
        if not data['employee_ids']:
            raise osv.except_osv(
                _("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(
                cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'payment_period': payment_period,
                'payroll_type': payroll_type,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}