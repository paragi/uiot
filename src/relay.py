# MicroPython ESP-32 relay driver
# Simon Rigét 2022 (c) MIT License
#
# GPIO pin assignment:
#    relay   gpio   Dev board pin
#    1       D23     37
#    2       D22     36
#    3       D21     33
#    4       D19     31
#    5       D18     30
#    6       D17     28
#    7       D16     27
#    8       D04     25

from common import *

try:
    from machine import Pin
    gpio = True
except Exception as e:
    gpio = False
    pass


class Relay:
    def __init__(self, relays):
        self.relays = relays
        self.inverse = True
        #     Pin, name
        self.relay = [
            {'pin': 23, 'name': "Relæ-1", 'function': None},
            {'pin': 22, 'name': "Relæ-2", 'function': None},
            {'pin': 21, 'name': "Relæ-3", 'function': None},
            {'pin': 19, 'name': "Relæ-4", 'function': None},
            {'pin': 18, 'name': "Relæ-5", 'function': None},
            {'pin': 17, 'name': "Relæ-6", 'function': None},
            {'pin': 16, 'name': "Relæ-7", 'function': None},
            {'pin':  4, 'name': "Relæ-8", 'function': None},
        ]

        for i in range(0, self.relays):
            if gpio:
                self.relay[i]['function'] = Pin(self.relay[i]['pin'], Pin.OUT).value
                self.set(i, 0)
            register_interaction('relay', str(i+1), self.handle_cmd)
            register_interaction('relay', self.relay[i]['name'], self.handle_cmd)
            debug("Init gpio for {} at pin {}".format(i, self.relay[i]['pin']), DEBUG)
        register_interaction('relay', 'all', self.handle_cmd)

    def set(self, relay_no, value):
        value ^= self.inverse
        if gpio and self.relay[relay_no]['function']:
            self.relay[relay_no]['function'](value)
        debug('Set {}({}) at pin {}: {}'.format(self.relay[relay_no]['name'], relay_no, self.relay[relay_no]['pin'], value) ,INFO)
        return value ^ self.inverse

    def get(self, relay_no):
        if gpio:
            value = self.relay[relay_no]['function']() ^ self.inverse
        else:
            value = -1
        debug('Get {}({}) at pin {}: {}'.format(self.relay[relay_no]['name'], relay_no, self.relay[relay_no]['pin'], value), INFO)
        return value ^ self.inverse

    def name(self, relay_no, name=None):
        if name:
            self.relay[relay_no]['name'] = name
        return self.relay[relay_no]['name']

    def handle_cmd(self, interaction, action):
        if not interaction or interaction == 'all':
            index = [ i for i in range(len(self.relay)) ]
        else:
            try:
                # by index
                index = [int(interaction)-1]
            except:
                # By name
                for i in range(len(self.relay)):
                    if interaction == self.relay[i]['name']:
                        index = [i]
                        break

        value = -1
        if action :
            if action == 'toggle':
                value = 2
            else:
                value = 1 if action.lower() in ('on', 'true', '1') else 0

        reply = ['ok']
        for i in index:
            if value < 0:
                rep = self.get(i)
            elif value == 2:
                rep = self.set(i, not self.get(i))
            else:
                rep = self.set(i, value)
            reply.append(f"{self.relay[i]['name']} {'on' if rep else 'off'}")

        if len(index) <= 0:
            reply = ['failed']

        return reply

app.relay = Relay(8)

if __name__ == '__main__':
    import time

    relay = Relay(8)
    for loop in range(1, 10):
        for i in range(0, relay.relays):
            relay.set(i, not relay.get(i))
            time.sleep(0.3)
