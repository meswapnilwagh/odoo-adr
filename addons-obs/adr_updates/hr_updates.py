# -*- coding: utf-8 -*-
"""
@author: Ernesto Mendez
"""

import logging
import time
from datetime import datetime
from dateutil import relativedelta
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class hr_recruitment_career(orm.Model):
    _name='hr.recruitment.career'
    _description = 'Carreras Profesionales'

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'sequence': fields.integer('Secuencia', size=2, required=True),
        }
hr_recruitment_career()

class hr_employee_emergency_contact(orm.Model):
    _name='hr.employee.emergency.contact'
    _description = 'Contacto de Emergencia'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', readonly=True),
        'name': fields.char('Nombre', size=64, required=True),
        'emergency_contact_phone': fields.char('Telefono', size=32)
    }
hr_employee_emergency_contact()

class hr_employee_ars(orm.Model):
    _name='hr.employee.ars'
    _description = 'Aseguradoras de Riesgos de Salud'

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'sequence': fields.integer('Secuencia', size=3, required=True)
    }

hr_employee_ars()


class hr_employee_family(orm.Model):
    _name="hr.employee.family"
    _description = 'Informacion Familiar'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleador'),
        'name': fields.char("Nombre", size=64, required=True),
        'relationship': fields.selection((('father', 'Padre'), ('mother', 'Madre'), ('daughter/son', 'Hijo/Hija'), ('other', 'Otro')), 'Parentesco'),
        'date_of_birth': fields.date('Fecha de Nacimiento', required=True, select=True),
        'gender': fields.selection((('male', 'Masculino'), ('female', 'Femenino')), 'Genero')
    }

hr_employee_family()

class ProffesionalFormation(orm.Model):

    _name = 'hr.employee.formation'
    _description = 'Formacion Profesional'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado'),
        'career_id': fields.many2one('hr.recruitment.career', 'Carrera'),
        'date_start': fields.date('Fecha de inicio'),
        'date_end': fields.date('Fecha de finalizacion'),
        'specialization': fields.char('Especializacion', size=128),
        'degree_id': fields.many2one('hr.recruitment.degree', 'Grado')
    }

class ProffesionalDegree(orm.Model):

    _name = 'hr.recruitment.degree'
    _description = 'Grados'
    _columns = {
        'name': fields.char('Grado', size=16, required=True),
        'sequence': fields.integer('Secuencia', size=16)
    }

ProffesionalDegree()

class hr_employee(orm.Model):
    _name='hr.employee'
    _inherit='hr.employee'

    _columns = {
        'partner_phone':fields.char('Telefono Personal', size=32),
        'emergency_contact':fields.one2many('hr.employee.emergency.contact', 'employee_id', 'Contactos de Emergencia'),
        'family_info_ids':fields.one2many('hr.employee.family', 'employee_id', 'Informacion Familiar'),
        'nss_id':fields.char('NSS', size=32),
        'hr_employee_ars_id':fields.many2one('hr.employee.ars', 'ARS Afiliado', required=False),
        'employee_code':fields.char('Codigo', size=32, required=True, readonly=True),
        'formation_ids': fields.one2many('hr.employee.formation', 'employee_id', 'Formacion', ondelete="cascade"),
    }

    _defaults = {
        'employee_code':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'employee.number')
    }

    def create(self, cr, uid, ids, context=None):
        """Overwritten to the create method of employee so that it creates a res_partner record as well."""

        partner_obj = self.pool.get('res.partner')
        values = ids
        created_id = super(hr_employee, self).create(cr, uid, values, context)
        created_partner_id = partner_obj.create(cr, uid, {'name': values.get('name'),
                                     'display_name': values.get('name_related'),
                                     'lang': 'es_DO',
                                     'active': True,
                                     'email': values.get('work_email'),
                                     'phone': values.get('work_phone'),
                                     'employee': True,
                                     'tz': 'America/Santo_Domingo',
                                     'notification_email_send': 'comment',
                                     'company_id': values.get('company_id')}, context)
        self.write(cr, uid, created_id, {'address_home_id': created_partner_id}, context)
        return created_id

hr_employee()

class hr_contract(orm.Model):
    _name='hr.contract'
    _inherit='hr.contract'

    def _get_contract_years(self, cr, uid, ids, name, arg, context=None):

        res = {}

        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = (dt2/365)
        return res

    def _get_contract_days(self, cr, uid, ids, name, arg, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = dt2
        return res

    _columns = {
        #'hr_contract_news_ids': fields.one2many('hr.contract.news', 'contract_id', 'Novedades del Contrato'),
        'schedule_pay': fields.selection([
            ('fortnightly', 'Quincenal'),
            ('monthly', 'Mensual'),
            ('quarterly', 'Trimestral'),
            ('semi-annually', 'Semestral'),
            ('annually', 'Anual'),
            ('weekly', 'Semanal'),
            ('bi-weekly', 'Bi-semanal'),
            ('bi-monthly', 'Bi-mensual'),
            ], 'Scheduled Pay', select=True),
#        'payroll_type': fields.selection([('administrative', 'Administrativa'),
#                                          ('educational', 'Educacional'),
#                                          ('vacations', 'Vacaciones'),
#                                          ('overtime', 'Horas Extras'),
#                                          ('xmas_bonus', 'Salario de Navidad')], 'Tipo de Nomina', required=True),
        'company_id': fields.many2one('res.company', 'Compañia', required=True),
        'contract_years': fields.function(_get_contract_years, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Años en el trabajo'),
        'contract_days': fields.function(_get_contract_days, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Dias en el trabajo'),

########################################################################################################################
        'pre_vac_coop_apply': fields.boolean('Aplicar?'),
        'pre_vac_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'pre_vac_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'pre_vac_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'pre_vac_coop_frecuency_number': fields.integer('Numero de Veces'),
        'pre_vac_coop_start_date': fields.date('Fecha Inicial'),
        'pre_vac_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'nav_coop_apply': fields.boolean('Aplicar?'),
        'nav_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'nav_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'nav_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'nav_coop_frecuency_number': fields.integer('Numero de Veces'),
        'nav_coop_start_date': fields.date('Fecha Inicial'),
        'nav_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'tel_tours_coop_apply': fields.boolean('Aplicar?'),
        'tel_tours_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'tel_tours_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'tel_tours_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'tel_tours_coop_frecuency_number': fields.integer('Numero de Veces'),
        'tel_tours_coop_start_date': fields.date('Fecha Inicial'),
        'tel_tours_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'prest_salud_apply': fields.boolean('Aplicar?'),
        'prest_salud_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_salud_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_salud_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_salud_frecuency_number': fields.integer('Numero de Veces'),
        'prest_salud_start_date': fields.date('Fecha Inicial'),
        'prest_salud_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'ahorro_coop_apply': fields.boolean('Aplicar?'),
        'ahorro_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'ahorro_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'ahorro_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'ahorro_coop_frecuency_number': fields.integer('Numero de Veces'),
        'ahorro_coop_start_date': fields.date('Fecha Inicial'),
        'ahorro_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'prest_normal_coop_apply': fields.boolean('Aplicar?'),
        'prest_normal_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_normal_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_normal_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_normal_coop_frecuency_number': fields.integer('Numero de Veces'),
        'prest_normal_coop_start_date': fields.date('Fecha Inicial'),
        'prest_normal_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'prest_tienda_coop_apply': fields.boolean('Aplicar?'),
        'prest_tienda_coop_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_tienda_coop_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_tienda_coop_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_tienda_coop_frecuency_number': fields.integer('Numero de Veces'),
        'prest_tienda_coop_start_date': fields.date('Fecha Inicial'),
        'prest_tienda_coop_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'seg_pre_ars_hum_apply': fields.boolean('Aplicar?'),
        'seg_pre_ars_hum_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'seg_pre_ars_hum_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'seg_pre_ars_hum_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'seg_pre_ars_hum_frecuency_number': fields.integer('Numero de Veces'),
        'seg_pre_ars_hum_start_date': fields.date('Fecha Inicial'),
        'seg_pre_ars_hum_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'seg_dep_adic_apply': fields.boolean('Aplicar?'),
        'seg_dep_adic_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'seg_dep_adic_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'seg_dep_adic_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'seg_dep_adic_frecuency_number': fields.integer('Numero de Veces'),
        'seg_dep_adic_start_date': fields.date('Fecha Inicial'),
        'seg_dep_adic_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'seg_vida_bhd_apply': fields.boolean('Aplicar?'),
        'seg_vida_bhd_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'seg_vida_bhd_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'seg_vida_bhd_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'seg_vida_bhd_frecuency_number': fields.integer('Numero de Veces'),
        'seg_vida_bhd_start_date': fields.date('Fecha Inicial'),
        'seg_vida_bhd_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'seg_vida_normal_apply': fields.boolean('Aplicar?'),
        'seg_vida_normal_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'seg_vida_normal_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'seg_vida_normal_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'seg_vida_normal_frecuency_number': fields.integer('Numero de Veces'),
        'seg_vida_normal_start_date': fields.date('Fecha Inicial'),
        'seg_vida_normal_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'prest_adr_apply': fields.boolean('Aplicar?'),
        'prest_adr_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_adr_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_adr_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_adr_frecuency_number': fields.integer('Numero de Veces'),
        'prest_adr_start_date': fields.date('Fecha Inicial'),
        'prest_adr_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'cxc_apply': fields.boolean('Aplicar?'),
        'cxc_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'cxc_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'cxc_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'cxc_frecuency_number': fields.integer('Numero de Veces'),
        'cxc_start_date': fields.date('Fecha Inicial'),
        'cxc_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'prest_vivienda_apply': fields.boolean('Aplicar?'),
        'prest_vivienda_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_vivienda_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_vivienda_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_vivienda_frecuency_number': fields.integer('Numero de Veces'),
        'prest_vivienda_start_date': fields.date('Fecha Inicial'),
        'prest_vivienda_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'fin_form_apply': fields.boolean('Aplicar?'),
        'fin_form_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'fin_form_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'fin_form_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'fin_form_frecuency_number': fields.integer('Numero de Veces'),
        'fin_form_start_date': fields.date('Fecha Inicial'),
        'fin_form_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'rifa_carro_apply': fields.boolean('Aplicar?'),
        'rifa_carro_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'rifa_carro_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'rifa_carro_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'rifa_carro_frecuency_number': fields.integer('Numero de Veces'),
        'rifa_carro_start_date': fields.date('Fecha Inicial'),
        'rifa_carro_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'cena_gala_apply': fields.boolean('Aplicar?'),
        'cena_gala_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'cena_gala_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'cena_gala_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'cena_gala_frecuency_number': fields.integer('Numero de Veces'),
        'cena_gala_start_date': fields.date('Fecha Inicial'),
        'cena_gala_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'cafeteria_apply': fields.boolean('Aplicar?'),
        'cafeteria_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'cafeteria_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'cafeteria_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'cafeteria_frecuency_number': fields.integer('Numero de Veces'),
        'cafeteria_start_date': fields.date('Fecha Inicial'),
        'cafeteria_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'memb_club_apply': fields.boolean('Aplicar?'),
        'memb_club_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'memb_club_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'memb_club_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'memb_club_frecuency_number': fields.integer('Numero de Veces'),
        'memb_club_start_date': fields.date('Fecha Inicial'),
        'memb_club_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'util_esc_apply': fields.boolean('Aplicar?'),
        'util_esc_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'util_esc_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'util_esc_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'util_esc_frecuency_number': fields.integer('Numero de Veces'),
        'util_esc_start_date': fields.date('Fecha Inicial'),
        'util_esc_end_date': fields.date('Fecha Final'),

########################################################################################################################
        'resort_apply': fields.boolean('Aplicar?'),
        'resort_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'resort_frecuency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'resort_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'resort_frecuency_number': fields.integer('Numero de Veces'),
        'resort_start_date': fields.date('Fecha Inicial'),
        'resort_end_date': fields.date('Fecha Final'),

        }

    _defaults = {
        'schedule_pay': 'fortnightly',
        'pre_vac_coop_frecuency_type' : 'fixed',
        'nav_coop_frecuency_type': 'fixed',
        'tel_tours_coop_frecuency_type': 'fixed',
        'prest_salud_frecuency_type': 'fixed',
        'ahorro_coop_frecuency_type': 'fixed',
        'prest_normal_coop_frecuency_type': 'fixed',
        'prest_tienda_coop_frecuency_type': 'fixed',
        'seg_pre_ars_hum_frecuency_type': 'fixed',
        'seg_dep_adic_frecuency_type': 'fixed',
        'seg_vida_bhd_frecuency_type': 'fixed',
        'seg_vida_normal_frecuency_type': 'fixed',
        'prest_adr_frecuency_type': 'fixed',
        'cxc_frecuency_type': 'fixed',
        'prest_vivienda_frecuency_type': 'fixed',
        'fin_form_frecuency_type': 'fixed',
        'rifa_carro_frecuency_type': 'fixed',
        'cena_gala_frecuency_type': 'fixed',
        'cafeteria_frecuency_type': 'fixed',
        'memb_club_frecuency_type': 'fixed',
        'util_esc_frecuency_type': 'fixed',
        'resort_frecuency_type': 'fixed',
    }

    def _check_dates_(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.pre_vac_coop_start_date > contract.pre_vac_coop_end_date:
                return False
            elif contract.nav_coop_start_date > contract.nav_coop_start_date:
                return False
        return True
