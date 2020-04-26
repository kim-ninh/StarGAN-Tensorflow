
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client import file, client, tools
from tqdm import tqdm

import httplib2
import os

check_point_dir = os.path.join('checkpoint',
                               'StarGAN_celebA_wgan-gp_6resblock_6dis')

SCOPES = 'https://www.googleapis.com/auth/drive'

# https://drive.google.com/drive/u/2/folders/1Hxosl5LZrxSn3LcDYm1JgPjuabHtjiQy
STARGAN_MODEL_FOLDER_ID = '1Hxosl5LZrxSn3LcDYm1JgPjuabHtjiQy'

store = file.Storage('storage.json')
# httplib2.debuglevel = 2                             # Enable debug log


def init():
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        creds = tools.run_flow(flow, store)
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(httplib2.Http()))
    return DRIVE


def upload_to_gdrive(drive, file_path: str):
    file_name = os.path.basename(file_path)
    DRIVE = drive

    file_metadata = {
        'name': file_name,
        'parents': [STARGAN_MODEL_FOLDER_ID]
    }
    media = MediaFileUpload(filename=file_path, resumable=True)

    uploaded = DRIVE.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print('File {} uploaded with ID: {}'.format(file_name, uploaded['id']))


if __name__ == '__main__':
    drive = init()

    model_files = [f for f in os.listdir(check_point_dir)
                   if os.path.isfile(os.path.join(check_point_dir, f))]

    for file in tqdm(model_files):
        upload_to_gdrive(drive, os.path.join(check_point_dir, file))
