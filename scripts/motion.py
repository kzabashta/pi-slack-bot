import RPi.GPIO as GPIO
import time
import os
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)
GPIO.setup(21, GPIO.OUT)

from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
client = SlackClient(slack_token)

while True:
       i=GPIO.input(23)
       if i==0:
             GPIO.output(21, 0)
             time.sleep(0.1)
       elif i==1:
             GPIO.output(21, 1)
             client.api_call(
              "chat.postMessage",
              channel="#general",
              text="motion detected"
             )
             time.sleep(60)
