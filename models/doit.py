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

        broken_dir = current_dir + '/../download/broken'
        path = current_dir + '/../download/stamm_reifen.csv'

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
                    if not os.path.exists(
                            os.path.join(broken_dir, 'stamm_' + value + '_' + str(grupe[value]) + '.csv')):
                        local = open(os.path.join(broken_dir, 'stamm_' + value + '_' + str(grupe[value]) + '.csv'), 'a',
                                     newline='')
                        writer = csv.writer(local, delimiter=';')
                        # write header at beginning of each broken csv file
                        writer.writerow(header)

                    # if file exists, open it to append next row
                    local = open(os.path.join(broken_dir, 'stamm_' + value + '_' + str(grupe[value]) + '.csv'), 'a',
                                 newline='')
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
        # get file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = current_dir + '/../download/stamm_reifen.csv'

        # prepare variables for reading
        reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
        header = next(reader)

        # counter
        i = 0

        # get all the criterias from product_importcriteria table
        sqlCriteria = "SELECT pa.name, ps.description, pav.name " \
                      "FROM product_attribute pa, product_searchoperators ps, product_importcriteria pi, product_attribute_value pav " \
                      "WHERE pi.attribute = pa.id AND pi.operator = ps.id AND pi.value = pav.id"
        self.env.cr.execute(sqlCriteria)
        criteria_results = self.env.cr.fetchall()

        # check rows in csv against criteria
        for row in reader:

            # if no criteria stored, all records will be imported
            if criteria_results is not None:
                # there is some criteria, run row through it
                if not self.run_filter_on_row(criteria_results, row, header):
                    # if criteria cannot be applied, skip to next row in csv
                    continue

            # prepare details array
            details_array = prepare_array(row, header)

            # if no barcode/EAN, no point to do other things, skip to another row in csv
            if details_array['barcode'] == '':
                continue

            # first, find id of product_template based on default_code or store new product_template
            prod_tmpl_id = self.find_record_in_table('product.template', 'default_code', details_array['default_code'])

            # if there is no product_template id with this articleNr
            if not prod_tmpl_id:
                # check also if there is record with guid
                if not self.find_record_in_table('product_template', 'guid', details_array['guid']):

                    # store one, automatically, record is stored in product_product too
                    prod_tmpl_id = self.store_values_in_table('product_template', details_array)

                    # store its attributes
                    ######################
                    self.store_attributes(row, header, prod_tmpl_id.id)

                else:
                    raise UserError('GUID %s found in table product_template, while default_code cannot be found!' % details_array['guid'])

            else:
                # update the attributes
                #######################

                # check if data in product_product is still the same
                ####################################################

                continue
            # check if barcode exists in product_product table
        #     if not (self.check_barcode(row[header.index('EAN')]) and self.check_GUID(row[header.index('NR')])):
        #         barcode = row[header.index('EAN')].strip()
        #         active = True
        #         default_code = row[header.index('ArtikelNr')]
        #         values_product_product = {
        #             'active': active,
        #             'barcode': barcode,
        #             'product_tmpl_id': prod_tmpl_id,
        #             'default_code': default_code
        #         }
        #
        #         self.store_values_in_table('product.product', values_product_product)
        #         i += 1
        #         # self.env.cr.execute(sql, (barcode, default_code, active, prod_tmpl_id))
        # if i == 1:
        #     show_message('Entered')
        # self.env.cr.commit()

        # self.env.invalidate_all()

    @api.multi
    def store_attributes(self, row, header, prod_tmpl_id):

        for head in header:
            value_of_attribute = row[header.index(head)].strip()

            # if cell in csv is empty, do not store attribute for product
            if value_of_attribute == '':
                continue

            # sql = "SELECT id FROM product_attribute WHERE name = %s"
            #
            # self.env.cr.execute(sql, (head,))
            # result = self.env.cr.fetchone()
            #
            # create_date = datetime.datetime.now()
            # write_date = create_date
            # create_uid = self._uid
            # write_uid = create_uid
            # get the id of the stored attribute
            product_attribute_id = self.find_record_in_table('product.attribute','name', head)

            # if it does not exists, move to the other head
            if not product_attribute_id:
                continue
            else:
                # check if the attribute-value pair already exist
                # product_attribute_id = result_id
                # self.env.cr.execute("SELECT id FROM product_attribute_value WHERE name = %s AND attribute_id = %s",
                #                     (value_of_attribute, product_attribute_id))
                #
                # match_found = self.env.cr.fetchone()

                match_found_id = self.find_record_in_table2('product.attribute.value','name', 'attribute_id', value_of_attribute, product_attribute_id)

                if not match_found_id:
                    # storing in product_attribute_value table if match attribute-value is not found
                    # self.env.cr.execute(
                    #     "INSERT INTO product_attribute_value(name, attribute_id, create_uid, create_date, write_uid, write_date) "
                    #     "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                    #     (value_of_attribute, product_attribute_id, create_uid, create_date, write_uid, write_date))
                    # self.env.cr.commit()

                    # self.env['product.attribute.value'].create(
                    #     {
                    #         'name': value_of_attribute,
                    #         'attribute_id': product_attribute_id,
                    #      }
                    # )
                    # self.env.cr.commit()
                    # show_message('tried')
                    # produ_attr_value_id = self.env.cr.fetchone()[0]

                    values = {
                            'name': value_of_attribute,
                            'attribute_id': product_attribute_id
                         }
                    result = self.store_values_in_table('product.attribute.value', values)
                    produ_attr_value_id = result.id
                else:
                    produ_attr_value_id = match_found_id

                # then store product_tmpl_id and attribute_id in table product_attribute_line
                try:
                    prod_attr_line_id = self.store_values_in_table('product.attribute.line', {'product_tmpl_id':prod_tmpl_id, 'attribute_id':product_attribute_id})
                except:
                    raise UserWarning('Error with storing in product.attribute.line')
                # self.env.cr.execute(
                #     "INSERT INTO product_attribute_line(product_tmpl_id, attribute_id, create_uid, create_date, write_uid, write_date) "
                #     "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                #     (prod_tmpl_id, product_attribute_id, create_uid, create_date, write_uid, write_date))
                # self.env.cr.commit()
                # prod_attr_line_id = self.env.cr.fetchone()[0]

                # finally, store product_attribute_line_id and product_attribute_value_id
                # in relation table product_attribute_line_product_attribute_value_rel
                try:
                    self.env.cr.execute(
                        "INSERT INTO product_attribute_line_product_attribute_value_rel (product_attribute_line_id, product_attribute_value_id) "
                        "VALUES (%s, %s)",
                        (prod_attr_line_id.id, produ_attr_value_id))
                    self.env.cr.commit()
                except:
                    raise UserWarning('Problem with %s %s' % (prod_attr_line_id.id, produ_attr_value_id))

    @api.multi
    def store_values_in_table(self, table, values):

        # make sure there is no underscore in table name
        if '_' in table:
            table = table.replace('_', '.')

        try:
            record = self.env[table].create(values)
            self.env.cr.commit()
        except:
            raise UserError('Probably duplicated GUID or default code!')

        return record

    @api.model
    def find_record_in_table(self, table, field, value):

        # make sure there is no dot in table name
        if '.' in table:
            table = table.replace('.', '_')

        # check if record exists on the basis of field and value
        # result_id = self.env[table].search([(field,'=',value)]).id

        sql = "SELECT id FROM " + table + " WHERE " + field + " = %s"

        self.env.cr.execute(sql, (value,))
        result = self.env.cr.fetchone()

        if result is None:
            return False
        else:
            return result[0]

    @api.model
    def find_record_in_table2(self, table, field, field2, value, value2):

        # make sure there is no dot in table name
        if '.' in table:
            table = table.replace('.', '_')

        # check if record exists on the basis of field and value
        # result_id = self.env[table].search([(field,'=',value)]).id

        sql = "SELECT id FROM " + table + " WHERE " + field + " = %s AND " + field2 + " = %s"

        self.env.cr.execute(sql, (value,value2,))
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
        intgroup = ('BREITE',)
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

    @api.model
    def get_category(self, name):
        sql = 'SELECT id FROM product_category WHERE name = %s'

        self.env.cr.execute(sql, (name,))
        self.env.cr.commit()
        result = self.env.cr.fetchone()

        if result is None:
            result = self.env['product.category'].create(
                {
                    'name': 'Tyres',
                    'complete_name': 'Tyres'
                }
            )
            self.env.cr.commit()
            return result.id
        else:
            return result[0]


def show_message(var, var2=None, var3=None):
    raise UserError(
        'variable is %s %s, second is %s %s, third is %s %s' % (var, type(var), var2, type(var2), var3, type(var3)))


def prepare_array(row, header):
    guid = row[header.index('NR')]
    ean = row[header.index('EAN')]
    default_code = row[header.index('ArtikelNr')]
    name = row[header.index('Profil')]

    return {'guid': guid,
            'barcode': ean,
            'default_code': default_code,
            'name': name
            }
