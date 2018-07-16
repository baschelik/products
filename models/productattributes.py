# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import Warning


class ProductAttributes(models.Model):
    _name = 'product.attribute'
    _inherit = 'product.attribute'

    # for overriding creation via GUI, adding custom fields and values
    # @api.model
    # def create(self, values):
    #     record = super(ProductAttributes, self).create(values)
    #     record['sequence'] = 2
    #     return record

    @api.model
    def import_attributes(self):
        columns = {'Gruppe', 'GruppeText', 'GruppeSymbol', 'EinsatzZweck', 'EinsatzZweckText', 'EinsatzZweckSymbol','EinsatzZweck2Text',
                   'DIMENSION', 'BREITE', 'HOEHE', 'BAUART', 'FELGE', 'LI', 'GI', 'GESCHW', 'TT_TL', 'Hersteller',
                   'HerstellerText', 'HerstellerSymbol','Profil', 'ProfilText', 'ProfilSymbol', 'LagerHoehe', 'Gewicht',
                   'ArtikelInfo4', 'ArtikelInfo5', 'ArtikelInfo6', 'ArtikelInfo7', 'DA', 'DEM', 'FR', 'ML', 'XL',
                   'AUSLAUF', 'DOT', 'PR', 'NOTLAUF1', 'Design1', 'Design2', 'Design3', 'Design4', 'Test1', 'Test2', 'Test3', 'Test4'}
        # variant = True
        # create_date = datetime.datetime.now()
        # write_date = create_date
        # create_uid = self._uid
        # write_uid = create_uid
        sqlFind = "SELECT id FROM product_attribute WHERE name = %s"
        i = 0

        # raise UserError('current user is %s' % self._uid)

        for column in columns:
            # check if attribute name already exists
            self.env.cr.execute(sqlFind, (column, ))
            result = self.env.cr.fetchone()

            if result is None:
                i += 1
                # this is much better way to store records
                # since it populates fields automatically, like create_date, create_uid, etc.
                self.env['product.attribute'].create(
                        {
                            'name': column,
                            'create_variant': True
                        }
                    )

                # sql = "INSERT INTO product_attribute(name, create_variant, create_uid, create_date, write_uid, write_date) VALUES(%s, %s, %s, %s, %s, %s)"
                # self.env.cr.execute(sql, (column, variant, create_uid, create_date, write_uid, write_date))
                self.env.cr.commit()
            else:
                continue

        raise Warning('Totally imported attributes %s' % i)

        # self.env['attributes'].create ({
        #     'name': 'Example'
        # })