import csv
import os
from odoo import models, fields, api
import logging
import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Doit(models.Model):
    _name = "doit"

    # with_ean = fields.Boolean()

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

        sql = "INSERT INTO product_product(barcode, default_code, active, product_tmpl_id) VALUES(%s, %s, %s, %s)"

        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        header = next(reader)

        i = 0

        # get all the criterias from product_importcriteria table
        sqlCriteria = "SELECT pa.name, ps.description, pi.value " \
                      "FROM product_importcriteria pi, product_searchoperators ps, product_attribute pa " \
                        "WHERE pi.attribute = pa.id AND pi.operator = ps.id"
        self.env.cr.execute(sqlCriteria)
        results = self.env.cr.fetchall()

        for row in reader:
            # if i == 10:
            #     show_message('Done 10 records')
            # if no criteria stored, all records will be imported
            if results is not None:
                # there is some criteria, prepare it for importing sql order
                check_row = self.run_filter_on_row(results, row, header)
                if not check_row:
                    continue

            i += 1
            # first, find id of product_template based on guid or store new product_template
            details_array = prepare_array(row, header)
            prod_tmpl_id = self.find_one_in_template(details_array['default_code'])

            # if there is no product_template id with this articleNr
            if not prod_tmpl_id:
                # store one
                prod_tmpl_id = self.store_one_in_template(details_array)

                # no EAN, skip to the next one
                if not prod_tmpl_id:
                    continue

                # store its attributes
                ######################
                self.store_attributes(row, header, prod_tmpl_id)


            # check if barcode exists in product_product table
            if not (self.check_barcode(row[header.index('EAN')]) and self.check_GUID(row[header.index('NR')])):
                active = True
                barcode = row[header.index('EAN')]
                default_code = row[header.index('ArtikelNr')]
                # guid = row[header.index('NR')]

                # this part will have to be implemented in cron view form, so that user choose to import
                # articles with or without EAN
                ##############################################################################################
                if barcode == '':
                    # this is in case we want to store articles without EAN
                    # active = False
                    # barcode = None

                    # this is in case we do not want to store articles without EAN
                    continue
                ###############################################################################################

                self.env.cr.execute(sql, (barcode, default_code, active, prod_tmpl_id))

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
        guid = details_array['guid']

        sql = "INSERT INTO product_template(name, default_code, type, categ_id, uom_id, uom_po_id, active, responsible_id, tracking, sale_line_warn, " \
              "purchase_line_warn, available_in_pos, guid) " \
              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"

        type = 'product'
        categ_id = self.get_category()
        if not categ_id: raise UserError('Could not find category Tyres when saving product_template!')
        uom_id = 1              # measure units, 1 is for units
        uom_po_id = 1           # measure units, 1 is for units
        responsible_id = 1
        tracking = 'none'
        sale_line_warn = 'no-message'
        purchase_line_warn = 'no-message'
        available_in_pos = True

        if ean == '':
            # no EAN, do not store it
            return False
        #     active = False
        else:
            active = True

        self.env.cr.execute(sql, (name, default_code, type, categ_id, uom_id, uom_po_id, active, responsible_id, tracking, sale_line_warn, purchase_line_warn, available_in_pos, guid))
        self.env.cr.commit()
        return self.env.cr.fetchone()[0]

    @api.multi
    def store_attributes(self, row, header, prod_tmpl_id):
        for head in header:
            sql = "SELECT id FROM product_attribute WHERE name = %s"

            self.env.cr.execute(sql, (head,))
            result = self.env.cr.fetchone()

            create_date = datetime.datetime.now()
            write_date = create_date
            create_uid = self._uid
            write_uid = create_uid
            value_of_attribute = row[header.index(head)].strip()

            if result is None:
                continue
            else:
                # if cell in csv is empty, do not store attribute for product
                if value_of_attribute == '':
                    continue

                # check if the attribute-value pair already exist
                product_attribute_id = result[0]
                self.env.cr.execute("SELECT id FROM product_attribute_value WHERE name = %s AND attribute_id = %s",
                                    (value_of_attribute, product_attribute_id))

                match_found = self.env.cr.fetchone()
                if match_found is None:
                    # storing in product_attribute_value table if match attribute-value is not found
                    self.env.cr.execute(
                        "INSERT INTO product_attribute_value(name, attribute_id, create_uid, create_date, write_uid, write_date) "
                        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                        (value_of_attribute, product_attribute_id, create_uid, create_date, write_uid, write_date))
                    self.env.cr.commit()

                    # self.env['product_attribute_value'].create(
                    #     {
                    #         'name': value_of_attribute,
                    #         'attribute_id': product_attribute_id,
                    #      }
                    # )
                    # self.env.cr.commit()
                    # show_message('tried')
                    produ_attr_value_id = self.env.cr.fetchone()[0]
                else:
                    produ_attr_value_id = match_found[0]

                # then store product_tmpl_id and attribute_id in table product_attribute_line
                self.env.cr.execute(
                    "INSERT INTO product_attribute_line(product_tmpl_id, attribute_id, create_uid, create_date, write_uid, write_date) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                    (prod_tmpl_id, product_attribute_id, create_uid, create_date, write_uid, write_date))
                self.env.cr.commit()
                prod_attr_line_id = self.env.cr.fetchone()[0]

                # finally, store product_attribute_line_id and product_attribute_value_id
                # in relation table product_attribute_line_product_attribute_value_rel
                self.env.cr.execute("INSERT INTO product_attribute_line_product_attribute_value_rel (product_attribute_line_id, product_attribute_value_id) "
                                    "VALUES (%s, %s)",
                                    (prod_attr_line_id, produ_attr_value_id))
                self.env.cr.commit()


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

    @api.model
    def check_barcode(self, barcode):
        if barcode == '':
            return False
        # check if default_code is in product_product
        sql = "SELECT id FROM product_product WHERE barcode = %s"

        self.env.cr.execute(sql, (barcode,))
        result = self.env.cr.fetchone()

        if result is None:
            return False
        else:
            return True

    @api.model
    def check_GUID(self, GUID):
        # check if default_code is in product_product
        sql = "SELECT id FROM product_template WHERE guid = %s"

        self.env.cr.execute(sql, (GUID,))
        result = self.env.cr.fetchone()

        if result is None:
            return False
        else:
            return True

    @api.model
    def run_filter_on_row(self, filters, row, header):
        # create tuples of attributes which can be strings or int
        intgroup = ('BREITE', )
        stringgroup = ('Gruppe',)

        # go through each filter
        for filter in filters:
            # get value from row under specific header field
            row_name_value = row[header.index(filter[0])]
            # if empty return false
            if row_name_value == '':
                return False
            # get operator from filter
            operator = filter[1]
            # get value from filter
            value = filter[2]
            # check whether criteria name is int or string
            if filter[0] in intgroup:
                # try to cast value to int
                try:
                    int(row_name_value)
                except:
                    # if not possible, return false
                    return False
                # join in string value, operator and header name
                operation = row_name_value + operator + value
                try:
                    # try to evaluate string expression
                    eval(operation)
                except:
                    raise UserWarning('Problem with %s %s' % (operation, int(row_name_value)))
                # string expression evaluates either true or false
                if not eval(operation):
                    return False
            # checking if it is string
            if filter[0] in stringgroup:
                if operator == '==':
                    if row_name_value != value:
                        return False

        return True


def show_message(var, var2 = None, var3 = None):
    raise UserError('variable is %s %s, second is %s %s, third is %s %s' % (var, type(var), var2, type(var2), var3, type(var3)))

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