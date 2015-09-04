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

from openerp import tools
from openerp import models, fields

class internal_requisition_report(models.Model):
    _name = "internal.requisition.report"
    _description = "Internal Requisition Statistics"
    _auto = False
    _rec_name = 'date'

    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_category_id = fields.Many2one('product.category', string='Category', readonly=True)
    price_total = fields.Float(string='Total Price', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    user_id = fields.Many2one('res.users', string='Requester', readonly=True)
    manager_id = fields.Many2one('res.users', string='Manager', readonly=True)

    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'internal_requisition_report')
        cr.execute("""create or replace view internal_requisition_report as (
            select
                min(ir.id) as id,
                ir.department_id as department_id,
                ir.user_id as user_id,
                pp.id as product_id,
                ir.date_start as date,
                pt.categ_id as product_category_id,
                sum(irl.price_unit) as price_total,
                ir.manager_id as manager_id,
                to_char(ir.date_start,'MM') as month 
            from
                internal_requisition ir
                left join internal_requisition_line irl on (irl.internal_requisition_id=ir.id)
                left join product_product pp on (pp.id=irl.product_id)
                left join product_template pt on (pt.id=pp.product_tmpl_id)
            group by
                department_id, product_id, product_category_id, user_id, pp.id, ir.manager_id, date
            )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: