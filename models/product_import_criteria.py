# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import os
import csv
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProductImportCriteria(models.Model):
    _name = 'product.importcriteria'

    name = fields.Char()
    operator = fields.Char()
    value = fields.Char()
    yesno = fields.Selection([('yes','Yes'), ('no','No')], string="Is this OK?")

