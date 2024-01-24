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
# Relay:      1  2  3  4  5  6  7  8
pinNumber = (23,22,21,19,18,17,16, 4)

from common import *

try:
    from machine import Pin
    gpio = True
except Exception as e:
    gpio = False
    pass


class Relay:
    def __init__(self):
        self.inverse = 1
        self.gpioPinControle = {}
        self.state = {}

        # Initialise GPIO pin
        assert(config['relay']['relays'])
        for i in range(1, str2int(config['relay']['relays'].value) + 1):
            if gpio and f'{i}-pin' in config['relay']:
                gpioPin = str2int(config['relay'][f'{i}-pin'].value)
                if gpioPin > 0:
                    self.gpioPinControle[i] = Pin(gpioPin, Pin.OUT).value
            self.state[i] = 0
            self.handleCmd(i, 'off')

    def handleCmd(self, interaction, action):
        reply = ''
        # Action -1=read, 0=off, 1=on, 2=toggle"
        value = -1
        if len(action):
            if action == 'toggle':
                value = 2
            else:
                value = 1 if action == 'on' else 0

        # Interaction can be a name, a number or 'all'
        relayNo = str2int(interaction)
        debug(f"Relay {interaction} {action}")
        for i in range(1, str2int(config['relay']['relays'].value) + 1):
            name = config['relay'][f'{i}-name'].value.lower()

            if interaction != 'all' and interaction != name and relayNo != i: continue
            if gpio and i in self.gpioPinControle:
                if value < 0 or value > 1:
                    # Get value
                    self.state[i] = self.gpioPinControle[i]() ^ self.inverse
                if value >= 0:
                    # Toggle
                    value = (self.state[i] ^ 1) if value > 1 else value
                    # Set value
                    self.state[i] = self.gpioPinControle[i](value ^ self.inverse)
            else:
                if value >= 0:
                    # Toggle
                    self.state[i] = (self.state[i] ^ 1) if value > 1 else value

            name = name if len(name) > 0 else str(relayNo)
            reply += f"\n{name} {'on' if self.state[i] else 'off'} "

        if len(reply):
            return "ok" + reply
        else:
            return f"failed\n '{interaction}' is an unknown interaction"
        debug(reply, INFO)

    def handlePresentation(self):
        presentation = {}
        for i in range(1, str2int(config['relay']['relays'].value) + 1):
            name = config['relay'][f'{i}-name'].value
            if gpio and i in self.gpioPinControle:
                self.state[i] = self.gpioPinControle[i]() ^ self.inverse
            debug(f"relay state {i}:{name} {self.state[i]}")
            presentation[name] = PresentationData(self.state[i], 'slider', f'relay {i} toggle')
        return presentation

# ------------  Module registration ------------
# All modules must register itself and attach  to the application

# Register factory cfgurations
# Usages: cfg.add( group or module name, name, type ('text'), alias, cfguratioon hint, advanced view only)
# Example cfg.add('relay', '1-name', 'text', 'Relæ-1', 'Name used to reference this interaction', True)

config.add('relay', 'relays', 'text', '8', 'Number of relays supported, starting with the forst one', True)

for i in range(1, str2int(config['relay']['relays'].value) +1):
    config.add('relay', f"{i}-name", 'text', f"Relæ-{i}", 'Name used to reference this interaction', False)
    config.add('relay', f"{i}-inverse", ['True','False'], 'True', 'Invers output og GPIO so that low=On Heigh=Off', True)
    config.add('relay', f"{i}-initial", ['off','on','last'], 0, 'Initial state of relay on startup', True)
    config.add('relay', f"{i}-pin", 'int', pinNumber[i-1], 'Pin number on GPIO', True)

# Attach to application
app.relay = Relay()

# Register interactions for this module and corresponding command handler

# Commands has the format: <context> [<interaction> [<action>]]
#   Context is usually the module name
#   Interaction is the name of the thing, unique within the context
#   Action is what to do with it

# The command handler is a function that handles commands sent to this module.
# If no interactions are needed, you can just register a command handler for this context
registerContext('relay', app.relay.handleCmd)

# What to show on the dashboard
app.dashboard['Relay'] = app.relay.handlePresentation

# Run this code, if run alone (for test purposes). Else ignore
if __name__ == '__main__':
    pass
