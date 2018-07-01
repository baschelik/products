# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    _sql_constraints = [
        ('GUID', 'unique(guid)', 'GUID must be unique!'),
        ('ArticleNr', 'unique(default_code)', 'ArticleNr must be unique!')
    ]

    guid = fields.Char()

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
    @api.multi
    def _do_it(self):
        _logger.debug('This is FDS email parsing and through we can parse the mail from any email')


