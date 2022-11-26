#!/usr/bin/env python
# Simon @paragi 2022

import gc
import random
from math import *
try:
    import asyncio
except:
    import uasyncio as asyncio

config = {}


class Dev:
    pass


class GPIO:
    def __init__(self):
        self.active = False
        try:
            print("Init GPIO")
            import machine
            import ubinascii
            id = str(ubinascii.hexlify(machine.unique_id()).decode('utf-8'))
            print("Machine ID:", id)
            self.led = machine.Pin(2, machine.Pin.OUT)
            self.led.value(0)
            self.active = True
        except Exception as e:
            print('-- GPIO init failed:', e)


try:
    print("Init ssd1306 display")
    import ssd1306
    import machine

    class DisplayOption(ssd1306.SSD1306_I2C):
        def __init__(self, width=128, height=64, type=None):
            self.active = False
            width, height = 128, 64
            self.font_height = 8
            self.font_width = 8
            i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
            super().__init__(width, height, i2c)
            self.type = 'SSD1306'
            self.active = True

except Exception as e:
    print('-- Failed', e)
    try:
        import tkinter

        class DisplayOption: # Tkinter replacement for PC
            BW = 1

            def __init__(self, width=128, height=64, type=None):
                print("Init display stub with tkinter")
                self.active = False
                self.font_height = 8
                self.font_width = 8
                self.width = width
                self.height = height
                self.window = tkinter.Tk()
                self.window.geometry("%dx%d" % (width, height))
                self.window_frame = tkinter.Frame()
                self.window_frame.master.title("OLED")
                self.window_frame.pack(fill=tkinter.BOTH, expand=1)
                self.canvas = tkinter.Canvas(self.window, width=width, height=height, bg="#000000")
                self.canvas.pack()
                self.img = tkinter.PhotoImage(width=width, height=height)
                self.canvas.create_image((width / 2, height / 2), image=self.img, state="normal")
                self.type = 'Display stub'
                self.active = True

            def pixel(self, x, y, col=1):
                value = ["black", "cyan"]
                self.img.put(value[int(bool(col))], (x, y))

            def show(self):
                self.window.update()

            def text(self, str, x, y, col=1):
                value = ["black", "cyan"]
                self.canvas.create_text(x + 1, y + 1, anchor=tkinter.NW, text=str, fill=value[int(bool(col))], font=('Helvetica 8'))

            def fill(self, col):
                self.canvas.delete("all")
                self.canvas.configure(bg=["black", "cyan"][int(bool(col))])
                self.img = tkinter.PhotoImage(width=self.width, height=self.height)
                self.canvas.create_image((self.width / 2, self.height / 2), image=self.img, state="normal")

    except Exception as e:
        print('-- Failed', e)

        class DisplayOption:
            def __init__(self, width=0, height=0, type=None):
                self.width = width
                self.height = height
                self.font_width
                self.font_height
                self.active = False

            def text(self, str, x, y, col):
                pass

            def fill(self, col):
                pass

            def show(self):
                pass

            def pixel(self, x, y, c=1):
                pass
finally:
    class Display(DisplayOption):
        def __init__(self, *args, **kwargs):
            super(Display, self).__init__(*args, **kwargs)
            self.text_x_center('whuha',20,0)
            self.text_x_center('whuha', 40, 1)

        def text_x_center(self, str, y=0, col=1):
            text_length = len(str)
            x = (self.width - 1 - text_length * self.font_width) // 2
            x = min(self.width - self.font_width - 1, max(0, x))
            y = min(self.height - self.font_height - 1, max(0, y))
            self.text(str, x, y, col)

        def show_logo(self):
            if self.active and self.width>0 and self.height>0:
                self.fill(0)
                resolution = radians(360 / self.width)
                for x in range(self.width):
                    y = int(self.height / 2 + self.height / 4 * sin(x * resolution))
                    self.pixel(x, y, 1)
                for x in range(self.width):
                    y = int(self.height / 2 + self.height / 5 * sin(x * resolution))
                    self.pixel(x, y, 1)
                for x in range(self.width):
                    y = int(self.height / 2 + self.height / 6 * sin(x * resolution))
                    self.pixel(x, y, 1)
                self.show()


class Network:
    def __init__(self):
        self.active = False
        self.nic = ''
        self.ip = ''
        self. ap = False
        self.lan = False
        self.wifi = False
        self.aaid = ''
        try:
            print('Using running network')
            try:
                import usocket as socket
            except Exception as e:
                import socket
            import fcntl
            import struct

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Fail if no network
            for nic_list in socket.if_nameindex():
                nic = nic_list[1]
                if nic == 'lo': continue
                self.nic = nic
                self.ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(nic[:15], 'utf-8')))[20:24])
                print('-- ', self.nic, self.ip)
                self.active = True

        except Exception as e:
            print('-- Failed', e)
            print('Connecting to Wifi')
            print('--Failed. Not configured')

            print('Init Access point on WiFi')
            try:
                import network
                import ubinascii
                try:
                    import usocket as socket
                except Exception as e:
                    import socket

                # Access point mode
                # Set up access point
                # Smartconfig https://www.eeweb.com/smartconfig-how-to-turn-an-esp8266-into-a-smart-home-device/
                if (not config['ssid'] or not config['wifi pw']) and not network.sta_if.active():
                    ssid = 'CP-IOT'  # Set access point name
                    # Generate simple random password for WiFi connection
                    pw = '0'.join([chr(int(random.getrandbits(5) / 1.23) + 97) for _ in range(4)] + ['1', '2', '3', '4'])
                    print('Setting up WiFi access point SSID: %s Password: %s' % ssid, pw)

                    if dev.display and dev.display.active:
                        dev.display.fill(0)
                        dev.display.text_x_center('Connect to WiFi', 0)
                        dev.display.text_x_center(ssid, dev.display.height // 4)
                        dev.display.text_x_center('Password:', dev.display.height // 2)
                        dev.display.text_x_center(pw, dev.display.height - dev.display.height // 4)
                        dev.display.show()

                    access_point = network.WLAN(network.access_point_IF)
                    access_point.active(True)
                    access_point.config(essid=ssid, password=pw)

                    print('Waiting for wifi AP')
                    while access_point.active() == False:
                        pass
                    print(access_point.ifconfig())
                    self.ap = True
                    self.ssid = ssid
                    self.active = True

            except Exception as e:
                print('-- Failed', e)


# ------------------------------------------------------------------------
def init_web_server(self):
    try:
        print('starting web server')
        import test_service_webserver
        asyncio.create_task(test_service_webserver())

    except Exception as e:
        print('-- Failed', e)


# Start services
async def service_blink():
    if dev.display.active or dev.gpio.active:
        while True:
            if dev.gpio.active:
                dev.gpio.led(1)
            else:
                dev.display.show_logo()
            await asyncio.sleep(1)
            if dev.gpio.active:
                dev.gpio.led(0)
            else:
                dev.display.fill(0)
                dev.display.show()
            await asyncio.sleep(1)


async def service_count():
    global c
    while True:
        # print(c)
        c += 1
        await asyncio.sleep(5)


import test_service_webserver


async def start_services():
    jobs = [
        asyncio.create_task(service_blink()),
        asyncio.create_task(service_count()),
        asyncio.create_task(service_webserver.start())
    ]
    for res in asyncio.as_completed(jobs):
        await res


if __name__ == '__main__':
    # Initialize devices
    def display_status(text):
        global dev
        print(text)
        if dev.display.active:
            dev.display.show_logo()
            dev.display.text_x_center('Init ' + text, 0)
            dev.display.show()

    dev = Dev()
    dev.gpio = GPIO()
    if dev.gpio.active:
        dev.gpio.led.value(1)
    dev.display = Display()
    display_status('Network')
    dev.network = Network()
    gc.collect()
    display_status('services')
    c = 1
    asyncio.run(start_services())
