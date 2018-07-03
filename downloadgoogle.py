"""
Shows basic usage of the Drive v3 API.

Creates a Drive v3 API service and prints the names and ids of the last 10 files
the user has access to.
"""
from __future__ import print_function
from googleapiclient.http import MediaIoBaseDownload
import io
from apiclient import errors
import smalltask

google_dir = 'download/from_drive/'
google_service = smalltask.authenticate()
page_token = None

smalltask.delete_files_in_folder(google_dir)

def download_csv(file_id, name):
    request = google_service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    with open(google_dir+name, 'wb') as output:
        output.write(fh.getvalue())

# # Call the Drive v3 API
# results = service.files().list(
#     pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get('files', [])
# if not items:
#     print('No files found.')
# else:
#     print('Files:')
#     for item in items:
#         print('{0} ({1})'.format(item['name'], item['id']))

# Finding all files in given folder ID
while True:
    try:
        # search for files located in folder (parents), with given ID, q determines criteria
        response = google_service.files().list(q="'1y9ebn_LKu8506wh4aPW1hTlK0jVwjcpD' in parents",
                                               spaces='drive',
                                               fields='nextPageToken, files(id, name)',
                                               pageToken=page_token).execute()

        for file in response.get('files', []):
            # Process change
            print('Found file: %s (%s) - %s' % (file.get('name'), file.get('id'), file.get('nextPageToken')))
            download_csv(file.get('id'), file.get('name'))
        page_token = response.get('nextPageToken', None)
        print(page_token)
        if page_token is None:
            break
    except errors.HttpError:
      print ('An error occurred: %s' % errors.HttpError)
      break
