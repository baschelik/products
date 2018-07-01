# -*- coding: utf-8 -*-

import os
from ftplib import FTP
import zipfile

def get_cartomak_csv():
    # set up initial variables
    url = 'data.cartomak.net'
    ftpuser = 'sell'
    ftppass = 'zauberlehrling'
    file_name = 'sell_supplier_compakt.zip'
    download_dir = 'download'
    local_filename = os.path.join(download_dir, file_name)

    # create directory if it does not exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # connect to FTP server
    ftp = FTP(url, ftpuser, ftppass)

    # create local file
    local_zip = open(local_filename, 'wb')

    try:
        # download file and put it in assigned directory
        ftp.retrbinary("RETR " + file_name, local_zip.write)
        ftp.close()
    except:
        print("Error with downloading the file or local folders")
        return False

    if os.path.exists(local_filename):
        print(local_filename, ' exists')
        # if under command is not put, zip file is recognized as badzip
        print(zipfile.is_zipfile(local_zip))

        # extract downloaded zip to download directory
        with zipfile.PyZipFile(local_filename, 'r') as zip_file:
            zip_file.extractall(download_dir)
            path_of_file = os.path.join(download_dir,zip_file.namelist()[0])

        # delete the zip
        os.remove(local_filename)

        return path_of_file

    else:
        return False