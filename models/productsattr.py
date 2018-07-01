# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import os
import csv
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProductAttr(models.Model):
    _name = 'product.details'
    # _inherit = 'product.product'
    _sql_constraints = [
        ('GUID', 'unique(guid)', 'GUID must be unique!'),
        ('GJ code', 'unique(default_code)', 'GJ ID must be unique!')
    ]


    product_tmpl_id = fields.Many2one('product.template', 'id', ondelete='cascade')

    guid = fields.Char()
    ean = fields.Char()
    gruppe = fields.Char()
    einsatz_zweck = fields.Char()
    brand = fields.Char()
    dimension = fields.Char()
    breite = fields.Char()
    hoehe = fields.Char()
    bauart = fields.Char()
    felge = fields.Char()
    li = fields.Char()
    gi = fields.Char()
    geschw = fields.Char()
    weight = fields.Char()
    default_code = fields.Char()

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
    @api.multi
    def _do_it(self):
        _logger.debug('This is FDS email parsing and through we can parse the mail from any email')

    @api.model
    def import_with_sql_details(self):
        # specify path manually, later it should be sent as argument
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = current_dir + '/../download/broken/stamm_PCR_177186.csv'

        # prepare sql statements
        sql_insert_row = "INSERT INTO product_details(guid, default_code, ean, gruppe, " \
                         "einsatz_zweck, brand, dimension, breite, hoehe, bauart," \
                         "felge, li, gi, geschw, weight) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s" \
                         ", %s, %s, %s, %s, %s, %s)"

        # read the csv file
        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        header = next(reader)

        for row in reader:
            # start with guid, check if it is already stored in table
            guid = row[header.index('NR')]
            # get category id for tyres
            category = self.get_category()
            if not category: category = 7
            # get ID of product.details, if that guid exists in table
            pd_id = self.guid_exists(guid)

            if not pd_id:
                details_array = prepare_array(guid, row, header, category)
                # try:
                    # check now via default_code, i.e. GoJames ID
                pt_id = self.check_default_code(details_array)
                get_logger(pt_id)

                # except:
                #     raise UserError('Problem with saving %s ' % details_array)

            name = row[header.index('Profil')]
            default_code = row[header.index('ArtikelNr')]

            # self.env.cr.execute(sql_insert_row, (guid, default_code, ean, gruppe,
            #                                      einsatz_zweck, brand, dimension, breite, hoehe, bauart,
            #                                      felge, li, gi, geschw, weight))

    @api.model
    def guid_exists(self, guid):
        # pure sql, much faster
        sql = "SELECT id FROM product_details WHERE guid = %s"

        self.env.cr.execute(sql, (guid,))
        exists = self.env.cr.fetchall()

        # self.env.invalidate_all()
        if len(exists) == 0:
            return False
        else:
            return exists[0][0]

    @api.model
    def get_category(self):
        sql = "select id from product_category where name = %s"

        self.env.cr.execute(sql, ['Tyres'])
        exists = self.env.cr.fetchall()

        # self.env.invalidate_all()
        if exists is None:
            return False
        else:
            return exists[0][0]

    @api.model
    def check_default_code(self, details_array):
        default_code = details_array['default_code']
        # pure sql, much faster
        sql = "SELECT id FROM product_template WHERE default_code = %s"
        self.env.cr.execute(sql, (default_code,))
        exists = self.env.cr.fetchone()

        if exists is None:
            #return id from newly created record in product_template
            return self.store_one_in_template(details_array)
        else:
            return exists[0]

    @api.model
    def store_one_in_template(self, details_array):
        sql = "INSERT INTO product_template(name, default_code, type, categ_id, uom_id, uom_po_id, active) " \
              "VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id"

        type = 'product'
        categ_id = 7
        uom_id = 1
        uom_po_id = 1
        active = True
        name = details_array['name']
        default_code = details_array['default_code']

        self.env.cr.execute(sql, (name, default_code, type, categ_id, uom_id, uom_po_id, active))
        self.env.cr.commit()
        return self.env.cr.fetchone()[0]


def prepare_array(guid, row, header, category):
    ean = row[header.index('EAN')]
    gruppe = row[header.index('Gruppe')]
    einsatz_zweck = row[header.index('EinsatzZweck')]
    dimension = row[header.index('DIMENSION')]
    brand = row[header.index('Hersteller')]
    breite = row[header.index('BREITE')]
    hoehe = row[header.index('HOEHE')]
    bauart = row[header.index('BAUART')]
    felge = row[header.index('FELGE')]
    li = row[header.index('LI')]
    gi = row[header.index('GI')]
    geschw = row[header.index('GESCHW')]
    name = row[header.index('Profil')]
    description = row[header.index('ProfilText')]
    type = 'product'
    weight = row[header.index('Gewicht')]
    default_code = row[header.index('ArtikelNr')]

    return {'guid': guid,
            'ean': ean,
            'gruppe': gruppe,
            'einsatz_zweck': einsatz_zweck,
            'dimension': dimension,
            'brand': brand,
            'breite': breite,
            'hoehe': hoehe,
            'bauart': bauart,
            'felge': felge,
            'li': li,
            'gi': gi,
            'geschw': geschw,
            'name': name,
            'description': description,
            'type': type,
            'categ_id': category,
            'weight': weight,
            'default_code': default_code,
            }

def get_logger(var):
    _logger.debug('here-------------------------------------')
    raise UserError('Details on variable %s %s' % (var, type(var)))
    # _logger.debug(var, type(var))
    _logger.debug('here-------------------------------------')
    exit()