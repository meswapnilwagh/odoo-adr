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

{
    'name' : 'Custom Validation on Purchase',
    'version' : '1.1',
    'category': 'Purchase Management',
    'depends' : ['base','purchase'],
    'author' : 'OBS',
    'description': """
Validación personalizada del flujo de compras para la Asociacion Dominicana de Rehabilitacion.-
===============================================================================================

En este módulo se modifica el flujo de trabajo de la compra con el fin de validar las compras
siguiente el flujo de trabajo de la ADR.
    """,
    'website': 'https://www.obsdr.com',
    'data': [
        'purchase_double_validation_workflow.xml',
        'purchase_double_validation_installer.xml',
        'purchase_double_validation_view.xml',
    ],
    'test': [
        'test/purchase_double_validation_demo.yml',
        'test/purchase_double_validation_test.yml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
