#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the res.bank object
#
#Author: Carlos Llamacho @ Open Business Solutions
#
#Date: 2013-10-23
#
#####

from openerp.osv import orm, fields


class ResBank(orm.Model):

    _inherit = 'res.bank'
    _columns = {
        'bank_check_digit': fields.selection((
            ('8', '8 - Banco Popular Dominicano'),
            ('5', '5 - Banco del Progreso'),
            ('8', '8 - Banco BHD'),
            ('6', '6 - Banco de Reservas'),
            ('4', '4 - Republic Bank'),
            ('5', '5 - Banco Leon'),
            ('4', '4 - Banco Santa Cruz'),
            ('1', '1 - Citibank'),
            ('0', '0 - Scotiabank'),
            ('9', '9 - Asociacion Popular de Ahorros y Prestamos'),
            ('9', '9 - Banco Lope de Haro'),
            ('8', '8 - BDI'),
            ('2', '2 - Banco Promerica'),
            ('1', '1 - Banco Caribe'),
            ('7', '7 - Asociacion Cibao de Ahorros y Prestamos')), 'Check Digit') }

ResBank()
