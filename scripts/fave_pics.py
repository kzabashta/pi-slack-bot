import os
import glob
import time
import datetime
import requests
import imageio

from datetime import datetime, date, time, timedelta

from slackclient import SlackClient

slack_token = os.environ["USER_SLACK_API_TOKEN"]

client = SlackClient(slack_token)


def get_channel():
    # get a list of channels
    channels = client.api_call('channels.list')['channels']

    # find a channel with the name motion
    return ([x for x in channels if x['name'] == "motion"])[0]['id']


def download_fave_pics():
    done = False
    latest_ts = time.time()
    channel_id = get_channel()

    while(not done):
        resp = client.api_call(
            'channels.history', channel=channel_id, latest=latest_ts)
        done = not resp['has_more']

        for msg in resp['messages']:
            latest_ts = msg['ts']
            if 'file' in msg:
                file = msg['file']
            if "reactions" in file:

                header = {
                    'Authorization': ('Bearer ' + slack_token)
                }

                r = requests.get(file['url_private_download'],
                                 headers=header, stream=True)

                with open((str(file['created']) + '_' + file['name']), 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

        print(
            datetime.datetime.fromtimestamp(float(latest_ts))
        )

    print("done")


def get_today_images():
    today_midnight = datetime.combine(date.today(), time.min)
    yesterday_midnight = today_midnight - timedelta(days=2)

    print(today_midnight)
    print(yesterday_midnight)

    done = False
    channel_id = get_channel()

    resp = client.api_call('channels.history', channel=channel_id,
                           latest=today_midnight.strftime('%s'),
                           oldest=yesterday_midnight.strftime('%s'))

    for msg in resp['messages']:
        print(msg)
        if 'file' in msg:
            file = msg['file']

            header = {
                'Authorization': ('Bearer ' + slack_token)
            }

            r = requests.get(file['url_private_download'],
                             headers=header, stream=True)

            with open((str(file['created']) + '_' + file['name']), 'wb') as f:
                for chunk in r:
                    f.write(chunk)

    print("done")


def stitch_animation():
    images = []
    for filename in glob.glob("*.jpg"):
        images.append(imageio.imread(filename))
    kargs = {'duration': 30}
    imageio.mimsave('movie.gif', images, duration=1)


if __name__ == '__main__':
    # download_fave_pics()
    # stitch_animation()

    get_today_images()
