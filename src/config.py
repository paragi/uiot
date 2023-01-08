# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license
import json
import os
from collections import OrderedDict

from common import *


class ConfigElement:
    def __init__(self, value=None, type=None, hint=None, advanced=None):
        self.value = value if value else ""
        self.type = type if type else "text"
        self.advanced = advanced if advanced else False
        self.hint = hint if hint else ""


# Numeric data types: int, float, complex
# String data types: str
# Sequence types: list, tuple, range
# Binary types: bytes, bytearray, memoryview
# Mapping data type: dict
# Boolean type: bool
# Set data types: set, frozenset
class Constraint:
    def type_text(element, length=-1):
        if isinstance(element, (list, tuple, range, dict)):
            return '0'
        if isinstance(element, str):
            return element[0:length if length >= 0 else len(element)]
        else:
            return str(element)[0:length if length >= 0 else len(str(element))]

    def type_int(element, min=None, max=None):
        i = int(element)
        if min:
            i = max(i, min)
        if max:
            i = min(i, min)
        return i

    def type_array(element):
        if isinstance(element, (list, tuple, range, dict)):
            return element
        if isinstance(element, (int, float, complex)):
            return [element]
        else:
            return [Constraint.type_text(element)]

    fit = {'text': type_text, 'password': type_text, 'int': type_int, 'array': type_array}

# Currently (2023) Micropython has issues with deriving subclass from a built in type.
# This class therefore use a variable to store the dict rather than self.
class Configure():
    class Setting(dict):
        def add(self, group, name, type='text', default='', hint='', advanced=False):
            debug(f"adding configuration:  {group}, {name}, {type}, {default}, {hint}, DEBUG)")
            # test constrains
            if group not in self:
                self[group] = {}
            if name in self[group] and self[group][name].value:
                value = self[group][name].value
            else:
                value = Constraint.fit[type](default)
            self[group][name] = ConfigElement(value, type, hint, advanced)

    def __init__(self):
        self.setting = Configure.Setting()
        self.retrieve()

    def retrieve(self):
        if 'config.json' in os.listdir():
            with open('config.json', 'r', encoding='utf-8') as f:
                array = json.loads(f.read())
                debug(f"Reading configuration: {array}", DEBUG)
                for group in array:
                    for field in array[group]:
                        self.setting.add(group, field, default=array[group][field])
                f.close()

    def store(self):
        array = {}
        with open('config.json', 'w', encoding='utf-8') as f:
            for group in self.setting:
                array[group] = {}
                for field in self.setting[group]:
                    array[group][field] = self.setting[group][field].value
            debug("Storing configuration: {}".format(array))
            json.dump(array, f)
            f.close()

    def factory_preset(self):
        debug("Deleting stored configuration")
        app.__init__()
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
            for group in self.setting:
                for field in self.setting[group]:
                    reply.append(f"{group} {field}={self.setting[group][field].value}")
        else:
            group, sep, field = interaction.partition('/')
            if len(group) and len(field):
                if action:
                    self.setting[group][field].value = action
                    reply = ['ok']
                else:
                    reply = ['ok']
                    reply.append(self.setting[group][field].value)
        return reply
