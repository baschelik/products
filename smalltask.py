# -*- coding: utf-8 -*-

import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dotenv import load_dotenv
from os.path import join, dirname

def delete_files_in_folder(folder_name):
    # create directory if it does not exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        # if folder exists, delete all files in it
        list(map(os.unlink, (os.path.join(folder_name, f) for f in os.listdir(folder_name))))


def authenticate():
    # Setup the Drive v3 API
    # Firstly, set up the scopes/permissions
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    # getting the credentials
    store = file.Storage('credentials.json')
    creds = store.get()
    # checking the credentials
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    return service

def get_sql_credentials():
    # prepare to read the env file
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # get connection info from .env file
    host = os.getenv('PS_HOST')
    port = os.getenv('PS_PORT')
    db = os.getenv('DB')
    user = os.getenv('PS_USER')
    password = os.getenv('PS_PASS')

    return {'host': host, 'port': port, 'db': db, 'user': user, 'password': password}

def get_logger(var):
    _logger.debug('here-------------------------------------')
    _logger.debug(var, type(var))
    exit()

def dd(var, var2 = None):
    print(var, var2, type(var), type(var2))
    exit()