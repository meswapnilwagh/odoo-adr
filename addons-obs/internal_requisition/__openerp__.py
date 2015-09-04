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
{
    'name' : 'Internal Requisition',
    'version' : '1.0',
    'category': 'Warehouse Management',
    'depends' : ['base', 'analytic_department', 'purchase', 'account_budget', 'sale_stock', 'hr'],
    'author' : 'Naresh Soni',
    'description': '''Internal Requisition Management ''',
    'website' : 'http://www.cozybizs.com',
    'data' : [
        'internal_requisition_sequence.xml',
        'wizard/internal_purchase_order.xml',
        'internal_requisition.xml',
        'internal_requisition_report.xml',
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'report/internal_requisition_report_view.xml',
        'views/report_internal_requisition.xml',
   ],
    'installable': True
}
