# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import os
import csv
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProductImportCriteria(models.Model):
    _name = 'product.importcriteria'

    # name = fields.Char()
    attribute = fields.Many2one('product.attribute', 'Attribute')
    operator = fields.Many2one('product.searchoperators', 'Operator')
    value = fields.Many2one('product.attribute.value', 'Value')
    # yesno = fields.Selection([('yes','Yes'), ('no','No')], string="Is this OK?")

    # @api.model
    # def create(self, values):
    #     raise Warning('values are %s' % values)
    #     record = super(ProductImportCriteria, self).create(values)
    #     record['attribute'] = 20
    #     return record
