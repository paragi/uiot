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
            {'pin': 23, 'name': "Relæ 1", 'value': None},
            {'pin': 22, 'name': "Relæ 3", 'value': None},
            {'pin': 21, 'name': "Relæ 3", 'value': None},
            {'pin': 19, 'name': "Relæ 4", 'value': None},
            {'pin': 18, 'name': "Relæ 5", 'value': None},
            {'pin': 17, 'name': "Relæ 6", 'value': None},
            {'pin': 16, 'name': "Relæ 7", 'value': None},
            {'pin':  4, 'name': "Relæ 8", 'value': None},
        ]
        self.init()

    def init(self):
        for i in range(0, self.relays):
            if gpio:
                self.relay[i]['value'] = Pin(self.relay[i]['pin'], Pin.OUT).value
                self.set(i, 0)
            debug("Init gpio for {} at pin {}".format(i, self.relay[i]['pin']), INFO)



    def set(self, relay_no, value):
        value ^= self.inverse
        if gpio:
            self.relay[relay_no]['value'](value)
        else:
            value = None
        debug('Set {}({}) at pin {}: {}'.format(self.relay[relay_no]['name'], relay_no, self.relay[relay_no]['pin'], value) ,INFO)
        return


    def get(self, relay_no):
        if gpio:
            value = self.relay[relay_no]['value']() ^ self.inverse
        else:
            value = None
        debug('Get {}({}) at pin {}: {}'.format(self.relay[relay_no]['name'], relay_no, self.relay[relay_no]['pin'], value), INFO)
        return value

    def name(self, relay_no, name=None):
        if name:
            self.relay[relay_no]['name'] = name
        return self.relay[relay_no]['name']

    def handle(self, interaction, action):
        k = -1
        try:
            k = int(interaction)
        except:
            for k, v in self.relay:
                if interaction == v.name:
                    break
        if k >= 0:
            if action:
                if action.lower() in ('on', 'true', '1'):
                    value = 1
                else:
                    value = 0
                self.set(k, value)
                return 'ok'
            else:
                return self.get(k)
        return 'failed'

relay = Relay(4)
register_context('relay', relay.handle)


if __name__ == '__main__':
    import time

    relay = Relay(8)
    for loop in range(1, 10):
        for i in range(0, relay.relays):
            relay.set(i, not relay.get(i))
            time.sleep(0.3)


            
