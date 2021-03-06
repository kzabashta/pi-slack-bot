from slackbot.bot import respond_to
from slackbot.bot import listen_to
from .rpi import temphumidity
import re

@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('I can understand hi or HI!')
    # react with thumb up emoji
    message.react('+1')

@respond_to('temperature', re.IGNORECASE)
def temperature(message):
    message.reply('Temperature is %sC' % (temphumidity.getTemperature()))

@respond_to('humidity', re.IGNORECASE)
def humidity(message):
    message.reply('Humidity is %s%%' % (temphumidity.getHumidity()))
