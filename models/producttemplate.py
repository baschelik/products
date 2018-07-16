# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    _sql_constraints = [
        ('GUID', 'unique(guid)', 'GUID must be unique!'),
        ('ArticleNr', 'unique(default_code)', 'ArticleNr must be unique!')
    ]

    guid = fields.Char()


    @api.model
    def create(self, values):
        # raise UserWarning('values are %s' % values)
        record = super(ProductTemplate, self).create(values)
        record['type'] = 'product'
        categ_id = self.env['product.category'].search(
            [
                (
                    'name',
                    '=',
                    'Tyres'
                )
            ]
        ).id

        if categ_id is False:
            raise UserError('Category Tyres is not defined!')
        record['categ_id'] = categ_id
        record['list_price'] = 0

        return record

