import json
import os
from common import *


class ConfigElement:
    def __init__(self, value=None, type=None, hint=None, advanced=None):
        self.value = value if value else ""
        self.type = type if type else "text"
        self.advanced = advanced if advanced else False
        self.hint = hint if hint else ""


class ConfigClass:
    def __init__(self):
        self.preset()
        self.retrieve()

    def preset(self):
        self.config = {
            'wifi': {
                # 'enable': ConfigElement('on', 'checkbox', "Enable: connect to existing WiFi. Disable to activate accespoint method"),
                'ssid': ConfigElement('', 'text', 'ID for access point/router (0 - 32 characters)'),
                'key': ConfigElement('', 'password', 'Authorisation key to gain access (0 - 63 characters)'),
            },
        }
        '''
            'access point':{
                'ssid': ConfigElement('CP-IOT', 'text', '', True),
                'key': ConfigElement('piratekey', 'password', '', True),
                'channel': ConfigElement('13', 'integer', '', True),
            },
            'security': {
                'configuration_change_enable': ConfigElement('off', 'checkbox', 'Enable simple password authentication for web access'),
                'password': ConfigElement('', 'password'),
            },
            'webserver': {
                'document_root': ConfigElement('/www', 'text', '', True),
                'host_ip': ConfigElement('0.0.0.0', 'text', '', True),
                'port': ConfigElement(80, 'integer', '', True),
            },
            'relay-1': {
                'name': ConfigElement('Relay-1', 'text', '', True),
                'pin': ConfigElement('22', 'text', '', True),
            },
            'relay-2': {
                'name': ConfigElement('Relay-2', 'text', '', True),
                'pin': ConfigElement('22', 'text', '', True),
            },
            'relay-3': {
                'name': ConfigElement('Relay-3', 'text', '', True),
                'pin': ConfigElement('22', 'text','', True),
            },
            'relay-4': {
                'name': ConfigElement('Relay-4', 'text', '', True),
                'pin': ConfigElement('22', 'text', '', True),
            },
        }
        '''

    def retrieve(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                array = json.loads(f.read())
                debug(f"Reading configuration: {array}", DEBUG)
                for group in array:
                    for field in array[group]:
                        self.config[group][field].value = array[group][field]
                f.close()
        except Exception as e:
            debug(f"Failed to read configuration: {e}", DEBUG)
            # self.store()

    def store(self):
        array = {}
        with open('config.json', 'w', encoding='utf-8') as f:
            for group in self.config:
                array[group] = {}
                for field in self.config[group]:
                    array[group][field] = self.config[group][field].value
            debug("Storing configuration: {}".format(array))
            json.dump(array, f)
            f.close()

    def factory_preset(self):
        debug("Deleting stored configuration")
        self.preset()
        return os.remove('config.json')

    def handle_cmd(self, interaction, action):
        reply = ['failed']
        if interaction in ['save', 'store']:
            self.store()
            reply = ['ok']
        elif interaction == 'factory_reset':
            self.factory_preset()
            reply = ['ok']
        elif interaction == 'all':
            reply = ['ok']
            for group in self.config:
                for field in self.config[group]:
                    reply.append(f"{group} {field}={self.config[group][field].value}")
        else:
            group, sep, field = interaction.partition('/')
            if len(group) and len(field):
                if action:
                    self.config[group][field].value = action
                    reply = ['ok']
                else:
                    reply = ['ok']
                    reply.append(self.config[group][field].value)
        return reply
