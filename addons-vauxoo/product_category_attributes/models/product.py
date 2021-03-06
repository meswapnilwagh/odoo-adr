# -*- encoding: utf-8 -*-
#
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Oalca (oscar@vauxoo.com)
#
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
from openerp.osv import osv, fields


class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'attribute_ids': fields.many2many('product.attribute',
                                          id1='category_att_id', id2='attr_id',
                                          string='Attributes'),

    }


class product_template(osv.osv):
    _inherit = 'product.template'
