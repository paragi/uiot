# Codinf Pirate micropython project
# By Simon Rigét @ paragi 2022
# Released under MIT licence

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
debug(level=DEBUG)

import uwebserver
import dynamic_pages
import relay

DELAY_RESTART_AP_S = 5
RETRY_CONNECT_EVERY_S = 60

class LAN:
  def __init__(self):
    self.client_ssid = ''
    self.client_key = ''
    self.client_ip = None

    self.ap_ssid = "CP-IOT"
    self.ap_key = b"piratekey"
    self.ap_ip = None
    self.keep_ap_active = False

    if platform != 'PC':
      # Always activate the interface before configuring it
      self.client_if = network.WLAN(network.STA_IF)
      self.client_if.active(False)
      self.ap_if = network.WLAN(network.AP_IF)
      self.ap_if.active(False)

  async def start_ap(self):
    debug("Setting up Access point")
    if  len(self.ap_ssid) and len(self.ap_key):
      self.ap_if.active(True)
      # self.ap_if.config(essid=self.ap_ssid, password=self.ap_key, authmode=network.AUTH_WPA_WPA2_PSK)
      self.ap_if.config(essid=self.ap_ssid, password=self.ap_key)
    try: # This sometimes fail with "RuntimeError: Wifi Unknown Error 0x5007"
      self.ap_if.ifconfig(("10.0.0.1", "255.255.255.0", "10.0.0.1", "10.0.0.1"))
    except: pass
    self.ap_ip = self.ap_if.ifconfig()[0]

    on_line = False
    while True:
      if self.client_if.isconnected() and not self.keep_ap_active:
        if on_line:
          self.ap_if.active(False)
          debug("Access point deactivated")
          on_line = False
      else:
        if not on_line:
          self.ap_if.active(True)
          on_line = True
          debug("-----------------------------------------------------------")
          debug(f"  Access point active at '{self.ap_ssid}' key: {self.ap_key}")
          debug(f"    server IP: {self.ap_ip}")
          debug("-----------------------------------------------------------")
      await asyncio.sleep(DELAY_RESTART_AP_S)


  async def start_client(self, ssid, key):
    if platform == 'PC':
      hostname = socket.gethostname()
      self.client_ip = socket.gethostbyname(hostname)
      debug("-----------------------------------------------------------")
      debug(f"  Using exixting network: '{hostname}' @ {self.client_ip}")
      debug("-----------------------------------------------------------")
      return

    self.client_ssid = ssid
    self.client_key = key
    if not len(self.client_ssid):
      debug("WiFi client not configured")
      return

    on_line = False
    while True:
      if self.client_if.isconnected():
        if not on_line:
          debug("-----------------------------------------------------------")
          debug(f"  Regained connection to Wifi '{self.client_ssid}'")
          debug(f"    server IP: {self.client_ip}")
          debug("-----------------------------------------------------------")
          on_line = True
          self.client_ip = self.client_if.ifconfig()[0]
      else:
        if on_line:
          debug(f"Lost connection to Wifi {self.client_ssid}")
          on_line = False

        debug(f"Try connecting to WiFi {self.client_ssid} with {self.client_key}")
        self.client_if.active(True)
        try:
          self.client_if.connect(self.client_ssid, self.client_key)
        except: pass

      await asyncio.sleep(DELAY_RESTART_AP_S)


task = {}

async def start_webserver_ap_wait_for_ip(lan):
  web_port = 8080 if platform == 'PC' else 80

  debug(f"Starting webserver for access point {lan.ap_ip}")
  while not lan.ap_ip:
    await asyncio.sleep(1)

  webserver = uwebserver.Webserver(host=lan.ap_ip, port=web_port, dyn_handler=dynamic_pages.page_handler, docroot='www')
  task = await webserver.start()
  debug("--------------------------------------------------")
  debug(f" Web server started for access point at http://{lan.ap_ip}:{web_port}")
  debug("--------------------------------------------------")
  return task

async def start_webserver_client_wait_for_ip(lan):
  web_port = 8080 if platform == 'PC' else 80

  debug(f"Starting webserver for LAN {lan.client_ip}")
  while not lan.client_ip:
    await asyncio.sleep(1)

  webserver = uwebserver.Webserver(host=lan.client_ip, port=web_port, dyn_handler=dynamic_pages.page_handler, docroot='www')
  task = await webserver.start()
  debug("--------------------------------------------------")
  debug(f" Web server started for WiFi client at http://{lan.client_ip}:{web_port}")
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
  task['lan_client'] = asyncio.create_task(lan.start_client(config['wifi']['ssid'].value, config['wifi']['key'].value))
  task['webserver_client'] = asyncio.create_task(start_webserver_client_wait_for_ip(lan))
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




asyncio.run(start_services())
