try:
    from machine import Pin, I2C
except:
    pass
try:
    from ssd1306 import SSD1306_I2C
except:
    pass
try:
    import usocket as socket  # importing socket
except:
    import socket
import network  # importing network
import esp  # importing ESP
import ubinascii
esp.osdebug(None)
import gc
import random
#import string
from math import *


class Display(SSD1306_I2C):
    def __init__(self):
        width, height = 128, 64
        self.font_height = 8
        self.font_width = 8

        i2c = I2C(scl=Pin(5), sda=Pin(4))
        super().__init__(width, height, i2c)

        self.text('Init 1', 0, 0)

        # Sinewave
        resolution = radians(360 / width)
        for x in range(width):
            y = int(height / 2 + height / 4 * sin(x * resolution))
            self.pixel(x, y, 1)
        for x in range(width):
            y = int(height / 2 + height / 5 * sin(x * resolution))
            self.pixel(x, y, 1)
        for x in range(width):
            y = int(height / 2 + height / 6 * sin(x * resolution))
            self.pixel(x, y, 1)
        self.show()

    def text_x_center(self, str, y=0, col=1):
        text_length = len(str)
        x = (self.width-1-text_length*self.font_width)//2
        x = min(self.width-self.font_width-1,max(0,x))
        y = min(self.height-self.font_height-1, max(0,y))
        self.text(str, x, y, col)

if __name__ == '__main__':
    # Initilaization

    # Led
    print("Init 1")
    led = Pin(2, Pin.OUT)
    led.value(0)

    # Display
    print("init 2")
    display = Display()
    led.value(1)
    display.text_x_center('Init 2', 0)
    display.show()
    gc.collect()

    # Network configuration
    # Hvis credentials: opret forbindelse
    # Hvis ikke forbindelse: opret forbindelse til fall back netværk
    # Ellers og Hvis ikke forbindelse: Opret Access Point
    display.fill(0)
    ssid = 'CP-IOT'  # Set access point name
    pw = '0'.join([chr(int(random.getrandbits(5) / 1.23) + 97) for _ in range(4)] + ['1','2','3','4'])

    display.text_x_center('Connect to WiFi', 0)
    display.text_x_center(ssid, display.height//4)
    display.text_x_center('Password:', display.height//2)
    display.text_x_center(pw, display.height - display.height//4)
    display.show()

    id = str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
    print("Machine ID:",id)

    access_point = network.WLAN(network.access_point_IF)
    access_point.active(True) 
    access_point.config(essid=ssid, password=pw)

    while access_point.active() == False:
        pass

    print('Connection is successful')
    print(access_point.ifconfig())

    display.fill(0)
    display.text_x_center('Init 3', 0)
    display.show()

    def web_page():
        html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
      <body><h1>Welcome to microcontrollerslab!</h1></body></html>"""
        return html


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket object
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        response = web_page()
        conn.send(response)
        conn.close()

    print("init 3")
