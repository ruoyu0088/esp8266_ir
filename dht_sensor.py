import dht
from machine import Pin


sensor = dht.DHT22(Pin(14))


def read():
    sensor.measure()
    temp = sensor.temperature()
    humid = sensor.humidity()
    return int(temp * 10), int(humid * 10)