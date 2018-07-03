from downloadean import get_ean_csv
# from downloadcsv import get_cartomak_csv
from importean import do_ean_import
# import glob
from import_initial import import_temp_basic_data
# import models
# from models import productsattr
from models.productsattr import ProductAttr
from smalltask import get_sql_credentials


# path = get_cartomak_csv()
# print(path)

# get_ean_csv()
# list_of_files = glob.glob(path+'*.csv')
# for value in list_of_files:
#     print('importing ', value)

# import_temp_basic_data()
# print(socket.gethostbyname(socket.gethostname()))

# productsattr.runi()
# ProductAttr.import_with_sql_details()
# print(get_sql_credentials())
exit()
# path = 'download/broken/stamm_PCR_177186.csv'
# do_ean_import(path)


# try to fill product.template with SQL commands
# import psycopg2
# import csv
#
# path = 'download/broken/stamm_PCR_177186.csv'
#
# conn_string = "dbname='murgic' host = '192.168.178.23' port='5432' user='odoo' password='odoo'"
# conn = psycopg2.connect(conn_string)
#
# sql = "INSERT INTO product_template(name, default_code, type, categ_id, uom_id, uom_po_id) VALUES(%s, %s, %s, %s, %s, %s)"
#
# reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
# header = next(reader)
# cur = conn.cursor()
# type = 'product'
#
# # get product category - name Tyres
# # field that cannot be null
# categ_id = 7
# uom_id = 1
# uom_po_id = 1
#
# for row in reader:
#     name = row[header.index('Profil')]
#     default_code = row[header.index('ArtikelNr')]
#
#
#     cur.execute(sql, (name, default_code, type, categ_id, uom_id, uom_po_id))
#
#     print('prepared to be committed')
#
#     conn.commit()
#
# cur.close()

# print("The number of parts: ", cur.rowcount)
#
# row = cur.fetchone()
#
# while row is not None:
#     print(row, type(row))
#     row = cur.fetchone()