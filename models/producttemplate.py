# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    # _sql_constraints = [
    #     ('GUID', 'unique(guid)', 'GUID must be unique!'),
    #     ('ArticleNr', 'unique(default_code)', 'ArticleNr must be unique!')
    # ]

    # guid = fields.Char()
    @api.model
    def create(self, values):
        raise UserWarning('values are %s' % values)
        record = super(ProductTemplate, self).create(values)
        record['attribute'] = 20
        return record

