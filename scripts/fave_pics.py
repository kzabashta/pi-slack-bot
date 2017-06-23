import os
import shutil
import glob
import time as t
import datetime
import requests
import imageio
import dropbox
from datetime import datetime, date, time, timedelta

from slackclient import SlackClient

SOURCE_CHANNEL = 'motion'
SLACK_TOKEN = os.environ['USER_SLACK_API_TOKEN']
DROPBOX_TOKEN = os.environ['DROPBOX_API_TOKEN']
IMAGES_DIR = 'images'
GIF_NAME = 'movements.gif'
CHUNK_SIZE = int(0.1 * 1024 * 1024)
RETRY_COUNT = 15

slack_client = SlackClient(SLACK_TOKEN)
dbox_client = dropbox.Dropbox(DROPBOX_TOKEN)

os.environ['TZ'] = 'US/Eastern'
t.tzset()


def init():
    if os.path.exists(IMAGES_DIR):
        shutil.rmtree(IMAGES_DIR)
    os.makedirs(IMAGES_DIR)

def get_channel():
    # get a list of channels
    channels = slack_client.api_call('channels.list')['channels']
    # find a channel with the name motion
    return ([x for x in channels if x['name'] == SOURCE_CHANNEL])[0]['id']


def handle_todays_pics(msg):
    if 'file' in msg:
        file = msg['file']

        header = {
            'Authorization': ('Bearer ' + SLACK_TOKEN)
        }

        r = requests.get(file['url_private_download'],
                         headers=header, stream=True)

        with open(os.path.join(IMAGES_DIR, (str(file['created']) + '_' + file['name'])), 'wb') as f:
            for chunk in r:
                f.write(chunk)


def handle_fave_pics(msg):
    if 'file' in msg:
        file = msg['file']
        if 'reactions' in file:

            header = {
                'Authorization': ('Bearer ' + SLACK_TOKEN)
            }

            r = requests.get(file['url_private_download'],
                             headers=header, stream=True)

            with open(os.path.join(IMAGES_DIR, (str(file['created']) + '_' + file['name'])), 'wb') as f:
                for chunk in r:
                    f.write(chunk)


def scrape_pics(fun, latest_ts=None, oldest_ts=None):
    done = False

    if latest_ts is None:
        latest_ts = t.time()
    if oldest_ts is None:
        oldest_ts = 0

    channel_id = get_channel()

    while(not done):
        resp = slack_client.api_call(
            'channels.history', channel=channel_id, latest=latest_ts, oldest=oldest_ts)
        done = not resp['has_more']

        for msg in resp['messages']:
            latest_ts = msg['ts']
            fun(msg)


def get_all_fave_pics():
    scrape_pics(handle_fave_pics)


def get_todays_pics():
    today_midnight = datetime.combine(date.today(), time.min)
    yesterday_midnight = today_midnight - timedelta(days=1)
    scrape_pics(handle_todays_pics, latest_ts=today_midnight.strftime('%s '), 
        oldest_ts=yesterday_midnight.strftime('%s'))

def upload_to_dropbox():
    f = open(os.path.join(IMAGES_DIR, GIF_NAME), 'rb')
    file_size = os.path.getsize(os.path.join(IMAGES_DIR, GIF_NAME))

    dest_fname = '/%s_%s' % (date.today().strftime('%Y_%m_%d'), GIF_NAME)

    try_count = 0
    while(try_count < RETRY_COUNT):
        try:
            upload_session_start_result = dbox_client.files_upload_session_start(f.read(CHUNK_SIZE))
            break
        except:
            try_count = try_count + 1
            t.sleep(5)
            print ('Attempting try %i out of %i' % (try_count, RETRY_COUNT))

    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                               offset=f.tell())
    commit = dropbox.files.CommitInfo(path=dest_fname)

    while f.tell() < file_size:
        if ((file_size - f.tell()) <= CHUNK_SIZE):
            dbox_client.files_upload_session_finish(f.read(CHUNK_SIZE),
                                            cursor,
                                            commit)
        else:
            try_count = 0
            while(try_count < RETRY_COUNT):
                try:
                    dbox_client.files_upload_session_append(f.read(CHUNK_SIZE),
                                                    cursor.session_id,
                                                    cursor.offset)
                    break
                except:
                    try_count = try_count + 1
                    t.sleep(5)
                    print ('Attempting try %i out of %i' % (try_count, RETRY_COUNT))
            cursor.offset = f.tell()
            print file_size - f.tell()

def stitch_animation():
    images = []
    for filename in sorted(glob.glob('%s/*.jpg' % IMAGES_DIR)):
        images.append(imageio.imread(filename))
    imageio.mimsave(os.path.join(IMAGES_DIR, GIF_NAME), images, duration=0.2,subrectangles=True)

if __name__ == '__main__':
    # hack until i figure out how to source env variables from bashrc
    while True:
        init()
        print("Getting today's pictures...")
        get_todays_pics()
        print("Creating a gif...")
        stitch_animation()
        print("Uploading to dropbox...")
        #upload_to_dropbox()
        t.sleep(86400)
