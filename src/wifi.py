# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license
import time
import gc

PC = 1
ESP = 2
try:
  import network
  import usocket as socket
  import uasyncio as asyncio
  import uselect as select
  platform = ESP
except:
  import socket
  import select
  import asyncio
  platform = PC

from common import *


DELAY_RESTART_AP_S = 5
RETRY_CONNECT_EVERY_S = 120
CONNECT_TIMEOUT_S = 20
READ_TIMEOUT_MS = 5000

if platform != PC:
  STATUS_TEXT = {
    network.STAT_IDLE: 'STAT_IDLE',
    network.STAT_CONNECTING: 'STAT_CONNECTING',
    network.STAT_WRONG_PASSWORD: 'STAT_WRONG_PASSWORD',
    network.STAT_NO_AP_FOUND: 'STAT_NO_AP_FOUND',
    # network.STAT_CONNECT_FAIL: 'STAT_CONNECT_FAIL',
    network.STAT_GOT_IP: 'STAT_GOT_IP'
  }


class Wifi:
  def __init__(self):
    self.MODE_CLIENT = 1
    self.MODE_AP = 2
    self.MODE_BOTH = 3
    self.MODE_FALLBACK_TO_AP = 4
    self.link_up = False
    self.link_permanently_down = False
    self.ap_down = True
    self.link_up_ip = None
    self.ip = {'client': None, 'access point': None}
    config.add('wifi', 'ssid', 'text', '', 'ID for access point/router (0 - 32 characters)', False)
    config.add('wifi', 'key', 'password', '', 'ID for access point/router (0 - 32 characters letters and numbers)', False)
    selection = ('Client only', 'Access point only', 'Both', 'Fallback to AP')
    config.add('wifi', 'mode', 'text', selection, 'ID for access point/router (0 - 32 characters letters and numbers)')
    config.add('wifi', 'ip', 'text', '', 'Static IP address (Ignoring DHCP from router)')
    config.add('wifi', 'gateway', 'text', '', 'Gateway IP address (Ignoring DHCP from router)', True)
    config.add('wifi', 'dns', 'text', '', 'DNS (Name server) IP address (Ignoring DHCP from router)'), True
    config.add('wifi', 'link_up_ip', 'text', '', 'IP address of server to ping for link-up test (Default gateway)', True)
    config.add('wifi', 'link_up_port', 'text', '', 'port to ping for link-up test (Default 80)', True)
    config.add('wifi', 'retry_connect_every_s', 'int', 30, 'Time between retry connecting to wifi', True)
    config.add('wifi', 'connect_timeout_s', 'int', 5, 'Timeout for connecting to wifi', True)
    config.add('wifi', 'read_timeout_s', 'int', 1, 'Timeout for socket reading (from clinet) in milli seconds', True)
    config.add('access point', 'ssid', 'text', 'CP_IOT', 'Network name for this device in access point modeo', False)
    config.add('access point', 'key', 'password', 'piratekey', 'Passphrase to connect to device ', False)
    selection = ['auto'] + [i for i in range(1,15)]
    config.add('access point', 'channel', 'text', selection, 'Wifi channel (Default auto select)', True)
    config.add('access point', 'ip', 'text', '', 'P address', True)
    if platform != PC:
      self.nic = network.WLAN(network.STA_IF)
      self.niap = network.WLAN(network.AP_IF)
      self.mode = self.MODE_FALLBACK_TO_AP
    else:
      self.mode = self.MODE_CLIENT


  async def is_link_up(self):
    global link_up_ip, link_up_port
    if not self.ip['client'] and not self.nic.isconnected():
      self.link_up = False
      return False
    if not self.link_up:
      return False
    if not self.link_up_ip:
      return True

    if len(link_up_ip) < 7 or link_up_ip == '0.0.0.0':
      link_up_ip = self.nic.ifconfig()[2] # Use gateway
    try:
      link_up_port = int(link_up_port)
    except:
      link_up_port = 80

    debug(f"Checking Wifi link at {self.nic.ifconfig()[2]}:{link_up_port}")
    try:
      reader, writer = await asyncio.open_connection(self.nic.ifconfig()[2], link_up_port)
      writer.write(b'GET / HTTP/1.0\r\n\r\n')
      await writer.drain()
      debug(await reader.readline(), DEBUG)
      writer.close()
      await writer.wait_closed()
      debug("Link is up")
      return True
    except OSError as e:
      debug(f"Link is down ({e})")

    return False

  def scan(self, best=False):
    if platform == PC: return
    import math

    debug("Scanning for WiFi networks, please wait...", INFO)

    authmodes = ('Open', 'WEP', 'WPA-PSK', 'WPA2-PSK4', 'WPA/WPA2-PSK', 'AUTH_WPA_WPA2_PSK', 'AUTH_MAX')
    channel = [
      {'ssid': '', 'bssid': '', 'signal': 0, 'interference': 0, 'authentication': '', 'hidden': '', 'best': ''}
      for i in range(0, 14)]
    interference = [0] * 14

    # if self.ap_if and self.ap_if.active():
    #    self.ap_if.active(False)

    # if not self.sta_if or not self.sta_if.active():
    self.sta_if = network.WLAN(network.STA_IF)
    self.sta_if.active(True)

    for (ssid, bssid, ch, db, authmode, hidden) in self.sta_if.scan():
      debug(f"{ch} Station {ssid} found", DEBUG)
      if 1 > ch > 14: continue
      channel[ch]['ssid'] = ssid
      channel[ch]['bssid'] = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid)
      channel[ch]['signal'] = db
      try:
        channel[ch]['authentication'] = authmodes[authmode]
      except:
        channel[ch]['authentication'] = f'Unknown ({authmode})'
      channel[ch]['hidden'] = ' hidden ' if hidden else ''

      for c in range(ch - 7, ch + 8):
        if c < 1: continue
        if c > 13: break
        # Approximate channel distance suppression
        channel_distance = abs(ch - c)
        suppression = (channel_distance - 3) * 5 + 20 if channel_distance > 2 else 0
        interference[c] += 10 ** ((db - suppression) / 10)

    best_channel = 1
    best_db = 1000
    for ch in range(1, 14):
      db = 10 * math.log10(interference[ch]) if interference[ch] > 0 else 0
      channel[ch]['interference'] = db
      if db < best_db:
        best_channel = ch
        best_db = db

    if best:
      return best_channel

    channel[best_channel]['best'] = '<=='
    debug(f"Best channel {best_channel} for AP. interference={best_db}db")

    # if debug_level >= INFO:
    row = "  ({:02}) SSID: {:20} - Auth: {:17} {} - Signal: {}db/{}db {}"
    for i in range(1, 14):
      debug(row.format(i, channel[i]['ssid'], channel[i]['authentication'], channel[i]['hidden'],
                       channel[i]['signal'], channel[i]['interference'], channel[i]['best']))

    return channel

  async def start(self):
    while True:
      if platform == PC:
        # This method of obtaining ip address may fail!
        hostname = socket.gethostname()
        self.ip['client'] = socket.gethostbyname(hostname)
        if self.ip['client']:
          self.link_up = True
        debug("-----------------------------------------------------------")
        debug(f"    Client IP:    {self.ip['client']}")
        debug("-----------------------------------------------------------")

      elif (not self.niap.active() or self.ap_down) and \
        ( self.mode == self.MODE_AP or
          self.mode == self.MODE_BOTH or
          (not self.link_up and self.mode == self.MODE_FALLBACK_TO_AP)
        ):
        self.niap.active(False)
        self.niap.active(True)
        # Default: ('192.168.4.1', '255.255.255.0', '192.168.4.1', '0.0.0.0')
        # try:  # This sometimes fail with "RuntimeError: Wifi Unknown Error 0x5007"
        # self.ap_if.ifconfig(('10.0.0.1', '255.255.255.0', '10.0.0.1', '0.0.0.0'))
        # self.ap_if.config(essid=self.ap_ssid, password=self.ap_key, authmode=network.AUTH_WPA_WPA2_PSK)
        # self.ap_if.config(essid=ssid, password=key, channel=channel, authmode=network.AUTH_WPA_WPA2_PSK)
        # self.ap_if.config(reconnects=5)
        self.niap.config(essid=config['access point']['ssid'].value, password=config['access point']['key'].value)
        self.ap_down = False
        # except:
        #  pass
        self.ip['access point'] = self.niap.ifconfig()[0]
        debug("-----------------------------------------------------------")
        debug(f"  Accesspoint at  '{config['access point']['ssid'].value}' password: '{config['access point']['key'].value}'")
        # debug(f"    Channel: {channel}")
        debug(f"    server IP: {self.ip['access point']}")
        debug("-----------------------------------------------------------")

      if platform != PC and not self.link_up and self.mode != self.MODE_AP and config['wifi']['ssid'].value:
        debug(f"Connecting to WiFi {config['wifi']['ssid'].value}")
        self.nic.active(False)
        await asyncio.sleep(1)
        self.nic.active(True)
        self.nic.connect(config['wifi']['ssid'].value, config['wifi']['key'].value)
        timeout = time.time() + CONNECT_TIMEOUT_S
        status = self.nic.status()
        while status == network.STAT_CONNECTING and timeout > time.time():
          status = self.nic.status()
          # print(status, self.nic.isconnected())
          await asyncio.sleep(0.5)
        if status == network.STAT_GOT_IP:
          if self.mode == self.MODE_FALLBACK_TO_AP:
            debug("Deactivating Access point")
            self.niap.active(False)
          ip = self.nic.ifconfig()
          debug("-----------------------------------------------------------")
          debug(f"  WiFi Connected to '{config['wifi']['ssid'].value}'")
          debug(f"    Client IP:    {ip[0]}")
          debug(f"    Subnet mask:  {ip[1]}")
          debug(f"    Gateway:      {ip[2]}")
          debug(f"    DNS:          {ip[3]}")
          debug("-----------------------------------------------------------")
          self.link_up = True
          self.ip['client'] = ip[0]
        elif status == network.STAT_WRONG_PASSWORD:
          self.link_permanently_down = True
          debug(f"Connection failed. Wrong password for {config['wifi']['ssid'].value}")
        elif status in STATUS_TEXT:
          debug(f"Connection failed. {STATUS_TEXT[status]}")
        else:
          debug(f"Connection failed. Unknown status ({status})")

      await asyncio.sleep(RETRY_CONNECT_EVERY_S)

      if self.mode != self.MODE_AP and self.link_up:
        print("Testinbg link")
        self.link_up = await self.is_link_up()
        gc.collect()


if 'wifi' not in app:
  app.wifi = Wifi()
  app.task['wifi'] = asyncio.create_task(app.wifi.start())