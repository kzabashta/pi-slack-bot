import RPi.GPIO as GPIO
import time
import os
import json
from datetime import datetime

from slackclient import SlackClient
import dropbox

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)

from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
client = SlackClient(slack_token)

def upload_photo():
       dbox_client = dropbox.client.DropboxClient(os.environ["DROPBOX_API_TOKEN"])
       print os.environ["DROPBOX_API_TOKEN"]
       fname = 'motion_%s.jpg' % datetime.now()
       f = open('/var/lib/motion/lastsnap.jpg', 'rb')
       response = dbox_client.put_file(fname, f)
       link = dbox_client.share(fname)['url']
       print(client.api_call('files.upload', channels="#general", filename='pic.jpg', file=open('/var/lib/motion/lastsnap.jpg', 'rb')))
       os.system('sudo rm -rf /var/lib/motion/*')
       client.api_call(
         "chat.postMessage",
         channel="#general",
         text="Motion Detected",
           attachments=json.dumps([{"title": "Cat", "color": "#36a64f", "title_link": link, "thumb_url": link}])
       )
       return link

def save_photo():
       os.system('curl http://localhost:8080/0/action/snapshot')
       time.sleep(5)

save_photo()
upload_photo()

while True:
       i=GPIO.input(23)
       if i==0:
             GPIO.output(21, 0)
             GPIO.output(20, 1)
             time.sleep(0.1)
       elif i==1:
             GPIO.output(21, 1)
             GPIO.output(20, 0)
             save_photo()
             upload_photo()
             time.sleep(60)
