#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the res_partner_bank object.
#
#Author: Carlos Llamacho @ Open Business Solutions
#
#Date: 2013-10-23
#
#####

from openerp.osv import orm, fields, osv


class ResPartnerBank(orm.Model):

    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'
    _columns = {
    'cod_operation': fields.selection((('22','Cr.Cta.Corriente'),
        ('32', '32 - Credito Cuenta de Ahorro'),
        ('52', '52 - Credito Prestamo/TCR'),
        ('42', '42 - Credito Cuenta Contable'),
        ('12', '12 - Emision de Cheques'),
        ('27', '27 - Debito Cuenta Corriente'),
        ('37', '37 - Debito Cuenta Ahorro'),
        ('57', '57 - Debito Tarjeta Credito'),
        ('47', '47 - Debito Cuenta Contable'),
        ('17', '17 - Debito Tarjeta Debito Popular'),
        ('28', '28 - Prenotificacion Debito Cuenta Corriente'),
        ('38', '38 - Prenotificacion Debito Cuenta Ahorro')),
    'Operation Code'),
    'bank_check_digit': fields.selection((('8', 'Banco Popular Dominicano'),
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
        ('7', '7 - Asociacion Cibao de Ahorros y Prestamos')),
    'Check Digit')
    }

    def onchange_bank_id(self, cr, uid, ids, bank_id, context=None):
        """On chaning the bank field pulls the bank check digit from the
        res.bank object. Then is added to the dict returned by the original
        method.

        Returns:
            True
        """
        bank_obj = self.pool.get('res.bank')
        if bank_id:
            result = super(ResPartnerBank, self).onchange_bank_id(cr, uid, ids,
                bank_id)
            bank = bank_obj.browse(cr, uid, bank_id)
            result['value']['bank_check_digit'] = bank.bank_check_digit
            return result

ResPartnerBank()
