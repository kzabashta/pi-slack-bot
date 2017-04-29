import RPi.GPIO as GPIO
from .sensor_utils import dht11

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin=4)
result = instance.read()
instance = dht11.DHT11(pin=4)

def getTemperature():
    result = instance.read()
    return result.temperature

def getHumidity():
    result = instance.read()
    return result.humidity
