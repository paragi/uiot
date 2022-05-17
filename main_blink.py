# https://docs.micropython.org/en/latest/esp32/quickref.html
from time import *
from machine import Pin

led = Pin(2, Pin.OUT)
led.value(0)
print("Hello")
while True:
    led.value(1)
    sleep(0.1)
    led.value(0)
    sleep(1)
