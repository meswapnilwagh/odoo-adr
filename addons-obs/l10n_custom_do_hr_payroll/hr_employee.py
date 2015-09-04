#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the hr.employee object.
#
#Author: Carlos Llamacho @ Open Business Solutions
#
#Date: 2013-10-22
#
#####

from openerp.osv import fields, orm


class EmployeeName(orm.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _auto = True
    _columns = {
    'names': fields.char('Primer y segundo nombre', size=128, required=True, help="""El primer y el segundo nombre del empleado."""),
    'first_lastname': fields.char('Primer apellido', size=64, required=True, help="""El primer apellido del empleado"""),
    'second_lastname': fields.char('Segundo Apellido', size=64, help="""El segundo apellido del empleado."""),
    'bank_id': fields.many2one('res.bank', 'Banco Nomina'),
    #'company_not_ret_agent': fields.boolean('Utiliza otro agente de retencion?', help='Marque este campo si el empleado cotiza a la TSS '
    #                                                                                  'a traves de otra Empresa'),
    #'company_ret_rnc_ced': fields.char('RNC/Cedula Agente de Retencion', 11,help='Agente de Retencion Unico de las '
    #                                                                             'Retenciones del Trabajador'),

    }

    def onchange_names(self, cr, uid, ids, names,
        first, last, context=None):
        """When there is change in the name of the employee
        concatenate the names with the first or second lastname and
        write the field name_related with it.

        Returns:
            True
        """
        res = {}
        if context is None:
            context = {}
            res = {'value':{'None'}}
        name = []
        if names:
            name.append(names)
        if first:
            name.append(first)
        if last:
            name.append(last)
        name = ' '.join(name)
        res['value'] = {'name': name}
        return res
