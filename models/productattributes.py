# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import csv
import os


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

            else:
                continue

        self.env.cr.commit()
        # raise Warning('Totally imported attributes %s' % i)

        # when all the attributes are set, then should go through EAN CSV file
        # ti import all the possible attributes vartiations

        # get file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = current_dir + '/../download/stamm_reifen.csv'

        # prepare variables for reading
        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        header = next(reader)

        for row in reader:
            for head in header:
                # does attribute exists in table product.attribute
                attribute_exists = self.env['product.attribute'].search(
                    [
                        (
                            'name',
                            '=',
                            head
                        )
                    ]
                )

                if not attribute_exists:
                    # not found, move to the next column title
                    continue
                else:
                    # found, store the attribute
                    value_of_attribute = row[header.index(head)].strip()

                    # if cell in csv is empty, do not store attribute for product
                    if value_of_attribute == '':
                        continue

                    # check if the attribute-value pair already exist
                    #########################################################################################
                    match_found_id = self.env['product.attribute.value'].search(
                        [
                            (
                                'name',
                                '=',
                                value_of_attribute
                            ),
                            (
                                'attribute_id',
                                '=',
                                attribute_exists.id
                            )
                        ]
                    )

                    # does not exist, store the pair: name of attribute and attribute_id
                    if not match_found_id:
                        result = self.env['product.attribute.value'].create(
                            {
                                'name': value_of_attribute,
                                'attribute_id': attribute_exists.id,
                                'sequence': 0
                            }
                        )
                        self.env.cr.commit()
                    else:
                        continue
                    #########################################################################################

            # show_message(attribute_exists.id, head)


def show_message(var, var2=None, var3=None):
    raise UserError(
        'variable is %s %s, second is %s %s, third is %s %s' % (var, type(var), var2, type(var2), var3, type(var3)))