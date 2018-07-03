# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductSearchOperators(models.Model):
    _name = 'product.searchoperators'

    name = fields.Char()
    description = fields.Char()
    # attribute = fields.Many2one('product.attribute', 'name')
    # operator = fields.Char()
    # value = fields.Char()
    # yesno = fields.Selection([('yes','Yes'), ('no','No')], string="Is this OK?")

