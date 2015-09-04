#-*- coding: utf-8 -*-
from openerp import models, fields, api, _


class res_company(models.Model):

    _inherit = 'res.company'
    
    code = fields.Char('Company Code',
                            required=False,
                            size=5)
