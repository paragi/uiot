import time

try:
  import network
  import usocket as socket
  import uasyncio as asyncio
  platform =  'ESP'
except:
  import socket
  import asyncio
  platform =  'PC'

import gc

from common import *
import uweb


DELAY_RESTART_AP_S = 5
RETRY_CONNECT_EVERY_S = 60

class LAN:
  def __init__(self):
    self.sta_ssid = "Network_not_found"
    self.sta_pw = "sommerhat."
    self.sta_ip = None

    self.ap_ssid = "CP-IOT"
    self.ap_pw = b"piratekey"
    self.ap_ip = None
    self.keep_ap_active = False

    if platform != 'PC':
      # Always activate the interface before configuring it
      self.sta_if = network.WLAN(network.STA_IF)
      self.sta_if.active(False)
      self.ap_if = network.WLAN(network.AP_IF)
      self.ap_if.active(False)

  async def start_ap(self):
    debug("Setting up Access point")
    if  len(self.ap_ssid) and len(self.ap_pw):
      self.ap_if.active(True)
      # self.ap_if.config(essid=self.ap_ssid, password=self.ap_pw, authmode=network.AUTH_WPA_WPA2_PSK)
      self.ap_if.config(essid=self.ap_ssid, password=self.ap_pw)
    try: # This sometimes fail with "RuntimeError: Wifi Unknown Error 0x5007"
      self.ap_if.ifconfig(("10.0.0.1", "255.255.255.0", "10.0.0.1", "10.0.0.1"))
    except: pass
    self.ap_ip = self.ap_if.ifconfig()[0]

    on_line = False
    while True:
      if self.sta_if.isconnected() and not self.keep_ap_active:
        if on_line:
          self.ap_if.active(False)
          debug("Access point deactivated")
          on_line = False
      else:
        if not on_line:
          self.ap_if.active(True)
          on_line = True
          debug("-----------------------------------------------------------")
          debug(f"  Access point active at '{self.ap_ssid}' key: {self.ap_pw}")
          debug(f"    server IP: {self.ap_ip}")
          debug("-----------------------------------------------------------")
      await asyncio.sleep(DELAY_RESTART_AP_S)


  async def start_sta(self):
    if platform == 'PC':
      hostname = socket.gethostname()
      self.sta_ip = socket.gethostbyname(hostname)
      debug("-----------------------------------------------------------")
      debug(f"  Using exixting network: '{hostname}' @ {self.sta_ip}")
      debug("-----------------------------------------------------------")
      return

    if not len(self.sta_ssid):
      debug("WiFi client not configured")
      return

    on_line = False
    while True:
      if self.sta_if.isconnected():
        if not on_line:
          debug("-----------------------------------------------------------")
          debug(f"  Regained connection to Wifi '{self.sta_ssid}'")
          debug(f"    server IP: {self.sta_ip}")
          debug("-----------------------------------------------------------")
          on_line = True
          self.sta_ip = self.sta_if.ifconfig()[0]
      else:
        if on_line:
          debug(f"Lost connection to Wifi {self.sta_ssid}")
          on_line = False

        debug(f"Try connecting to WiFi {self.sta_ssid} with {self.sta_pw}")
        self.sta_if.active(True)
        try:
          self.sta_if.connect(self.sta_ssid, self.sta_pw)
        except: pass

      await asyncio.sleep(DELAY_RESTART_AP_S)


async def web_page(request):
  header = 'HTTP/1.x 200 OK\r\n'\
  'Content-Type: text/html; charset=UTF-8\r\n'\
  'Content-Length: {}\r\n'\
  '\r\n'

  body = """<!DOCTYPE html>
  <html>
  <head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body>
  <h1>CP-IOT Laboratories</h1>
  <img src="logo.gif">
  <form method="POST">
  <label>input<input type="text" name="test" value="test"></label>
  <button type="submit">Send</button>
  </form>
  </body>
  </html>\r\n\r\n"""
  return header.format(len(body)-1) + body

task = {}


async def start_webserver_ap_wait_for_ip(lan):
  web_port = 8080 if platform == 'PC' else 80

  debug(f"Starting webserver for access point {lan.ap_ip}")
  while not lan.ap_ip:
    await asyncio.sleep(1)

  webserver = uweb.Webserver(host=lan.ap_ip, port=web_port, dyn_handler=web_page, docroot='/www')
  # webserver_sta = uweb.Webserver(host=lan.sta_ip, port=web_port,  docroot='www')
  task = await webserver.start()
  debug("--------------------------------------------------")
  debug(f" Web server started for access point at http://{lan.ap_ip}:{web_port}")
  debug("--------------------------------------------------")
  return task

async def start_webserver_sta_wait_for_ip(lan):
  web_port = 8080 if platform == 'PC' else 80

  debug(f"Starting webserver for LAN {lan.sta_ip}")
  while not lan.sta_ip:
    await asyncio.sleep(1)

  webserver = uweb.Webserver(host=lan.sta_ip, port=web_port, dyn_handler=web_page, docroot='www')
  # webserver_sta = uweb.Webserver(host=lan.sta_ip, port=web_port,  docroot='./www')
  task = await webserver.start()
  debug("--------------------------------------------------")
  debug(f" Web server started for WiFi client at http://{lan.sta_ip}:{web_port}")
  debug("--------------------------------------------------")
  return task

async def blink_start():
  print("Starting blink service")
  try:
    import machine
    led = machine.Pin(2, machine.Pin.OUT)
    while True:
      led.value(not led.value())
      await asyncio.sleep(0.5)
      # print(".", end='')

  except Exception as e:
    print("LED Blink service failed")

async def start_services():
  lan = LAN()
  lan.keep_ap_active = True
  task['lan_sta'] = asyncio.create_task(lan.start_sta())
  task['webserver_sta'] = asyncio.create_task(start_webserver_sta_wait_for_ip(lan))
  if platform != 'PC':
    task['lan_ap'] = asyncio.create_task(lan.start_ap())
    task['webserver_ap'] = asyncio.create_task(start_webserver_ap_wait_for_ip(lan))

  gc.collect()
  # start other services here
  task['blink'] = asyncio.create_task(blink_start())
  print("All tasks started")

  while True:
    await asyncio.sleep(10)
    gc.collect()


debug(level=DEBUG)
asyncio.run(start_services())
