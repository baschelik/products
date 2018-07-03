# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProductAttributes(models.Model):
    _name = 'product.attribute'
    _inherit = 'product.attribute'
    #
    # yip = fields.Char()

    @api.multi
    def _do_it(self):
        _logger.debug('This is FDS email parsing and through we can parse the mail from any email')


    # for overriding creation via GUI, adding custom fields and values
    # @api.model
    # def create(self, values):
    #     record = super(ProductAttributes, self).create(values)
    #     record['sequence'] = 2
    #     return record

    @api.model
    def import_attributes(self):
        columns = {'Gruppe', 'GruppeText', 'GruppeSymbol', 'EinsatzZweck', 'EinsatzZweckText', 'EinsatzZweckSymbol',
                   'Dimension', 'Breite', 'Hoehe', 'Bauart', 'Felge', 'LI', 'GI', 'Geschw', 'TT_TL', 'Hersteller',
                   'HerstellerText', 'HerstellerSymbol','Profil', 'ProfilText', 'ProfilSymbol', 'LagerHoehe', 'Gewicht'}
        variant = True
        create_date = datetime.datetime.now()
        write_date = create_date
        create_uid = self._uid
        write_uid = create_uid

        # raise UserError('current user is %s' % self._uid)

        for column in columns:
            sql = "INSERT INTO product_attribute(name, create_variant, create_uid, create_date, write_uid, write_date) VALUES(%s, %s, %s, %s, %s, %s)"
            self.env.cr.execute(sql, (column, variant, create_uid, create_date, write_uid, write_date))

        self.env.cr.commit()

        # self.env['attributes'].create ({
        #     'name': 'Example'
        # })