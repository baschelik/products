# -*- coding: utf-8 -*-
import csv
import xmlrpc.client
import os
from os.path import join, dirname
from dotenv import load_dotenv
from odoo.exceptions import UserError
import sys
import psycopg2
import time

conn_string = "dbname='murgic' host = '192.168.178.23' port='5432' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)

# prepare to read the env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# get connection info from .env file
url = os.getenv('URL')
db = os.getenv('DB')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# connect to odoo database
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

# get uid, if false, something is wrong with credentials
uid = common.authenticate(db, username, password, {})

# connect to database object with odoo
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# get product category - name Tyres
category = models.execute_kw(db, uid, password,
                             'product.category', 'search',
                             [[['name', '=', 'Tyres']]])

def do_ean_import(path):
    # read a csv file, in this case it is file with guid and ean
    reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
    row_count = len(open(path).readlines())
    # store/skip header
    header = next(reader)
    i = 0
    start_time = time.time()

    # read csv line by line
    for row in reader:
        # i += 1
        # sys.stdout.write(str(i))
        # sys.stdout.write("\r%d%%" % int(i / row_count))
        # sys.stdout.flush()

        # take elements from list, based on index of elements in header
        guid = row[header.index('NR')]
        # get ID of product.details, if that guid exists in table
        pd_id = guid_exists(guid)

        # if there is no guid in product.details
        if not pd_id:

            # i += 1

            details_array = prepare_array(guid, row, header)

            # insert 1 new record to product.template and 1 to product details
            try:
                # new_record_template = store_new_product_template(details_array['name'], details_array['default_code'])

                # check now via default_code, i.e. GoJames ID
                pt_id = check_default_code(details_array['default_code'])

                details_array.update({'product_tmpl_id': pt_id})

                new_record = store_new_product_details(details_array)

                print('new record stored')

            except:
                raise UserError('Problem with saving %s ' % details_array['default_code'])

        # there is GUID, check before updating if there is record in product.template
        else:
            i += 1
            detail_complete = models.execute_kw(db, uid, password,
                                                'product.details', 'read', [pd_id])
            details_array = prepare_array(guid, row, header)

            # what to do in case details do not contain product_tmpl_id
            if not check_fk(detail_complete):
                # check now via default_code, i.e. GoJames ID
                pt_id = check_default_code(detail_complete[0]['default_code'])

                # in case template is not found even with default_code
                # create new entry
                if not pt_id:
                    new_record_template = store_new_product_template(details_array['name'],
                                                                     details_array['default_code'])
                    details_array.update({'product_tmpl_id': new_record_template, 'id': pd_id})
                    # update details with product template id and send details id to know what record to update
                    update_new_product_details(details_array)
                    print('ovdje 1. put kad ne moze naci ni fk ni code')
                else:
                    details_array.update({'product_tmpl_id': pt_id, 'id': pd_id})
                    update_new_product_details(details_array)
                    print('ovdje 2. put')

            else:
                # just update entry in details from row in csv
                details_array.update({'id': pd_id})
                update_new_product_details(details_array)
                print('updated')

    # get time of execution
    print('Total seconds execution is %s' % (time.time() - start_time))


def guid_exists(guid):
    exists = models.execute_kw(db, uid, password,
                      'product.details', 'search',
                      [[['guid', '=', guid]]])
    if not exists:
        return False
    else:
        return exists[0]


def prepare_array(guid, row, header):
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
    categ_id = category[0]
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
            'categ_id': categ_id,
            'weight': weight,
            'default_code': default_code,
            }


def store_new_product_template(name, default_code):
    return models.execute_kw(db, uid, password, 'product.template', 'create', [{
        'name': name,
        'default_code': default_code,
        'type': 'product'
    }])

def store_new_product_details(details_array):
    return models.execute_kw(db, uid, password, 'product.details', 'create', [details_array])


def update_new_product_details(details_array):
    id = details_array['id']
    del details_array['id']
    return models.execute_kw(db, uid, password, 'product.details', 'write', [[id], details_array])


def check_fk(detail_complete):
    # here, I have to check if the record is stored in product_template
    product_tmpl_id = detail_complete[0]['product_tmpl_id']

    if not product_tmpl_id:
        return False
    else:
        return product_tmpl_id[0]


def check_default_code(default_code):
    # here, I have to check if the record is stored in product_template
    # xmlrpc way, very slow
    # exists = models.execute_kw(db, uid, password,
    #                            'product.template', 'search',
    #                            [[['default_code', '=', default_code]]])

    # pure sql, much faster
    sql = "SELECT * FROM product_template WHERE default_code = %s"
    cur = conn.cursor()
    cur.execute(sql, (default_code,))
    exists = cur.fetchone()

    if exists is None:
        return False
    else:
        return exists[0]
