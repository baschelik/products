import csv
import os
from odoo import models, fields, api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Doit(models.Model):
    _name = "doit"

    # zip = fields.Integer()

    @api.model
    def break_ean(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        broken_dir = current_dir+'/../download/broken'
        path = current_dir+'/../download/stamm_reifen.csv'

        # read a csv file, in this case it is file with guid and ean
        # for ean file, mandatory define encoding as latin-1, otherwise error when reading the original file
        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        # store/skip header
        header = next(reader)
        grupe = {}

        # read line by line csv file
        for row in reader:
            # grab text in the column Gruppe
            gruppe = row[header.index('Gruppe')]

            # if it is blank string, call it EMPTY
            if gruppe == '':
                gruppe = 'EMPTY'

            # if gruppe is not yet in array grupe, add it and assign value of 0
            if gruppe not in grupe:
                grupe[gruppe] = 0
            # else increase the count of gruppe type for 1
            else:
                grupe[gruppe] += 1


        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        # store/skip header and move reader to row 2, to actual data
        header = next(reader)

        # create directory if it does not exists
        if not os.path.exists(broken_dir):
            os.makedirs(broken_dir)
        else:
            # if folder exists, delete all files in it
            list(map(os.unlink, (os.path.join(broken_dir, f) for f in os.listdir(broken_dir))))

        # read line by line csv file
        for row in reader:
            # go through the array grupe
            for value in grupe:
                # grab text in the column Gruppe
                gruppe = row[header.index('Gruppe')]

                # this is in case that ean is empty
                # thus, files will be much smaller
                ean = row[header.index('EAN')]
                if ean is '':
                    continue

                # when csv column and array value match
                if gruppe == value:
                    # if csv file does not exists, create it with name,
                    # which contains type of tyre and total number of rows found for this tyre type
                    if not os.path.exists(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv')):
                        local = open(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv'), 'a', newline='')
                        writer = csv.writer(local, delimiter=';')
                        # write header at beginning of each broken csv file
                        writer.writerow(header)

                    # if file exists, open it to append next row
                    local = open(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv'), 'a', newline='')
                    writer = csv.writer(local, delimiter=';')
                    writer.writerow(row)

    @api.multi
    def give_msg(self):
        _logger.debug('new window should be created..........................')
        return {
            'name': 'Breaking EAN completed',
            'domain': [],
            'res_model': 'doit',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'new',
        }

    @api.model
    def import_with_sql(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = current_dir + '/../download/stamm_reifen.csv'

        sql = "INSERT INTO product_product(barcode, default_code, guid, active, product_tmpl_id) VALUES(%s, %s, %s, %s, %s)"

        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        header = next(reader)

        i = 0

        for row in reader:
            i += 1
            # first, find id of product_template based on guid or store new product_template
            details_array = prepare_array(row, header)
            prod_tmpl_id = self.find_one_in_template(details_array['default_code'])

            # if there is no product_template id with this articleNr
            if not prod_tmpl_id:
                prod_tmpl_id = self.store_one_in_template(details_array)

            active = True
            barcode = row[header.index('EAN')]
            default_code = row[header.index('ArtikelNr')]
            guid = row[header.index('NR')]
            if barcode == '':
                active = False
                barcode = None

            self.env.cr.execute(sql, (barcode, default_code, guid, active, prod_tmpl_id))

        self.env.cr.commit()

        # self.env.invalidate_all()

    @api.model
    def get_category(self):
        sql = "select id from product_category where name = %s"

        self.env.cr.execute(sql, ['Tyres'])
        exists = self.env.cr.fetchone()

        # self.env.invalidate_all()
        if exists is None:
            return False
        else:
            return exists[0]

    @api.model
    def store_one_in_template(self, details_array):
        default_code = details_array['default_code']
        name = details_array['name']
        ean = details_array['ean']

        sql = "INSERT INTO product_template(name, default_code, type, categ_id, uom_id, uom_po_id, active) " \
              "VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id"

        type = 'product'
        categ_id = self.get_category()
        if not categ_id: raise UserError('Could not find category Tyres when saving product_template!')
        uom_id = 1              # measure units, 1 is for units
        uom_po_id = 1           # measure units, 1 is for units
        if ean == '':
            active = False
        else:
            active = True

        self.env.cr.execute(sql, (name, default_code, type, categ_id, uom_id, uom_po_id, active))
        self.env.cr.commit()
        return self.env.cr.fetchone()[0]

    @api.model
    def find_one_in_template(self, default_code):
        # check if default_code is in product_product
        sql = "SELECT id FROM product_template WHERE default_code = %s"

        self.env.cr.execute(sql, (default_code,))
        result = self.env.cr.fetchone()

        if result is None:
            return False
        else:
            return result[0]


def show_message(var, var2 = None):
    raise UserError('variable is %s %s, second is %s %s' % (var, type(var), var2, type(var2)))

def prepare_array(row, header):
    guid = row[header.index('NR')]
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
            'weight': weight,
            'default_code': default_code,
            }