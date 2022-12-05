import network
import time
import sys
try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from common import *


class Wifi:
    def __int__(self):
        self.ap = None
        self.sta = None
        self.ip = 'None'
        self.mask = ''
        self.gateway = ''
        self.dns = ''
        self.last_ssid = None
        self.last_key = None


    def ap(self, ssid=None, key=None, channel=None):
        if not ssid: ssid = "Pirate cove"
        if not key:  key = b"pirate key"
        if not channel or 1 > channel > 13: channel = self.scan(best=True)
        debug(f"Creating WiFI access point {ssid} at channel {channel}")
        #if self.sta and self.sta.active():
        #    self.sta.active(False)
        self.ap = network.WLAN(network.AP_IF)
        try:
            if type(key) == 'str': key = key.encode('UTF-8')
            # self.ap.config(reconnects=5)
            self.ap.ifconfig(('10.0.0.1', '255.255.255.0', '10.0.0.1', '10.0.0.1'))
            self.ap.config(essid=ssid, password=key, channel=channel,authmode=network.AUTH_WPA_WPA2_PSK)
            self.ap.active(True)
            nc = self.ap.ifconfig()
            debug(f'Network interface settings: {nc[0]}</br>{nc[1]}</br>{nc[2]}</br>{nc[3]}')
        except Exception as e:
            debug(f"Unable to create access point: {e}", ERROR)
            self.ip = ''
            return False

        (self.ip, self.mask, self.gateway, self.dns) = self.ap.ifconfig()
        debug("+------------------------------------------+")
        debug("   Acces point: ")
        debug(f"   SSID: {ssid} at channel {channel}")
        debug("   KEY: " + str(key))
        debug(f"   IP: {self.ip}")
        debug("+------------------------------------------+")
        return True

    def connect(self, ssid, key):
        debug(f"Connecting to WiFI {ssid} ")
        # if self.ap :
        #    self.ap.active(False)
        self.sta = network.WLAN(network.STA_IF)
        if self.sta and self.sta.isconnected() and ssid == self.sta.config('essid'):
            debug(f"Already connected to {ssid}")
            return True
        self.sta.active(True)
        debug(f"connecting to {ssid} key:{key}", DEBUG)
        self.sta.connect(ssid, key)

        start = time.ticks_ms()
        while not self.sta.isconnected():
            time.sleep(0.1)
            if start - time.ticks_ms() > 5000:
                debug(f"Failed to connect to {ssid}")
                return False

        (self.ip, self.mask, self.gateway, self.dns) = self.sta.ifconfig()
        debug("+------------------------------------------+")
        debug("   WiFi connected to:")
        debug(f"   SSID: {ssid} ")
        debug(f"   IP: {self.ip}")
        debug("+------------------------------------------+")
        self.last_ssid = ssid
        self.last_key = key
        return True

    def scan(self, best=False):
        import math

        debug("Scanning for WiFi networks, please wait...", INFO)

        authmodes = ('Open', 'WEP', 'WPA-PSK', 'WPA2-PSK4', 'WPA/WPA2-PSK', 'AUTH_WPA_WPA2_PSK', 'AUTH_MAX')
        channel = [
            {'ssid': '', 'bssid': '', 'signal': 0, 'interference': 0, 'authentication': '', 'hidden': '', 'best': ''}
            for i in range(0, 14)]
        interference = [0] * 14

        # if self.ap and self.ap.active():
        #    self.ap.active(False)

        #if not self.sta or not self.sta.active():
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)

        for (ssid, bssid, ch, db, authmode, hidden) in self.sta.scan():
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
        debug("Starting network service")
        while True:
            if not self.sta.isconnected():
                debug("Wifi connection failed. retrying")
                self.connect(self, self.last_ssid, self.last_key)
            else:
                # Test internet connection
                # test time
                pass
            await asyncio.sleep(5)