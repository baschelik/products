# try to fill product.template with SQL commands
import psycopg2
import csv

def import_temp_basic_data():
    path = 'download/broken/stamm_PCR_177186.csv'

    conn_string = "dbname='murgic' host = 'postgresql' port='5432' user='odoo' password='odoo'"
    conn = psycopg2.connect(conn_string)

    sql = "INSERT INTO product_template(name, default_code, type, categ_id, uom_id, uom_po_id, active) VALUES(%s, %s, %s, %s, %s, %s, %s)"

    reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
    header = next(reader)
    cur = conn.cursor()
    type = 'product'

    # get product category - name Tyres
    # field that cannot be null
    categ_id = 7
    uom_id = 1
    uom_po_id = 1
    active = True

    i = 0

    for row in reader:
        i += 1
        name = row[header.index('Profil')]
        default_code = row[header.index('ArtikelNr')]


        cur.execute(sql, (name, default_code, type, categ_id, uom_id, uom_po_id, active))

        print('prepared to be committed ', i)

        conn.commit()

    cur.close()