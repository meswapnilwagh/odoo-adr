#-*- coding: utf-8 -*-

from openerp import models, fields, api, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Category code',
                            required=True,
                            size=10)
    sequence_id = fields.Many2one('ir.sequence',
                                       string='Category sequence',
                                       required=True)
    
    @api.model
    def create(self, vals):
        created_id = super(ProductCategory, self).create(vals)
        seq_id = self.get_created_seq_id(created_id.id)
        created_id.write({'sequence_id': seq_id.id})
        return created_id
    
    def get_created_seq_id(self, product_category_id):        
        category_name = self.env['product.category'].browse(product_category_id).name
        sequence = self.env['ir.sequence']
        created_seq_id = sequence.create({
            'name': 'Code {0}'.format(category_name),
            'active': True,
            'code': 'product.category.code',
            'padding': 5,
            'number_increment': 1,
            'next_number': 1,
            'implementation': 'no_gap'})
        return created_seq_id    


class Product(models.Model):
    _inherit = 'product.product'

    def get_category_code(self):
        seq_obj = self.env['ir.sequence']
        for product in self:
            category = product.product_tmpl_id.categ_id
            name = category.name
            code = category.code
            seq_id = seq_obj.search([('name', '=', 'Code {0}'.format(name))], limit=1)
            if code and seq_id:
                seq_number = seq_obj.get_id(seq_id.id)
                seq_number = seq_number.strip()
                if product.product_tmpl_id.type in ('product', 'consu') and product.product_tmpl_id.company_id.code:
                    res = {product.id: product.product_tmpl_id.company_id.code + '_' + code + seq_number}
                else:
                    res = {product.id: code + seq_number}
            else:
                res = {product.id: False}
        return res
    
    @api.model
    def create(self, vals):
        created_id = super(Product, self).create(vals)
        code = created_id.get_category_code()
        created_id.write({'default_code': code.get(created_id.id)})
        return created_id
    
    @api.multi
    def write(self, values):
        sequence = self.env['ir.sequence']
        product_category = self.env['product.category']
#         product = self.env['product.product']
#         product_ids = product.search([('default_sale','=',True)])
        if values.has_key('categ_id'):
            category = product_category.browse(values['categ_id'])
            category_name = category.name
            category_code = category.code
            
            new_seq_id = sequence.search([('name', '=', 'Code {0}'.format(category_name))], limit=1)
            new_sequence = sequence.get_id(new_seq_id.id)
            if new_sequence:
                new_sequence = new_sequence.strip()
                if self.product_tmpl_id.type in ('product', 'consu') and self.product_tmpl_id.company_id.code:
                    new_sequence = self.product_tmpl_id.company_id.code + '_' + category_code + new_sequence
                else:
                    new_sequence = category_code + new_sequence
            values['default_code'] = new_sequence
        
        super(Product, self).write(values)
        return True

    default_code = fields.Char(string='Internal reference', size=32)
