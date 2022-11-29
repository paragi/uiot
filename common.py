# Common elements to this project

import json


# Degug level
SILENT = 0
ERROR = 1
WARNING = 2
INFO = 3    # Default level
DEBUG = 4
debug_level = SILENT


def debug(msg = None, msg_level = None, level = None):
    global debug_level
    level_str = ('','Error','Warning','Info','Debug')
    if level and isinstance(level, int) and SILENT < level <= DEBUG:
        debug_level = level
    if not msg_level or type(msg_level) != 'int':
        msg_level = INFO
    if msg and msg_level <= debug_level and debug_level > SILENT:
        print(level_str[msg_level] + ':', msg)


class ConfigElement:
        def __init__(self, value=None, type=None):
            self.value = value if value else ""
            self.type = type if type else "text"


# Default/factory configuration
config = {
    'wifi': {
        'enable': ConfigElement('off', 'checkbox'),
        'ssid': ConfigElement('<SSID>', 'text'),
        'key': ConfigElement('<KEY>', 'password')
    },
    'access point':{
        'enable': ConfigElement('on', 'checkbox'),
        'ssid': ConfigElement('CP-IOT', 'text'),
        'key': ConfigElement('pirate', 'password')
    },
    'security': {
        'configuration change enable': ConfigElement('on', 'checkbox'),
        'password': ConfigElement('', 'password'),
    },
    'webserver': {
        'document root': ConfigElement('/www', 'text'),
        'host ip': ConfigElement('0.0.0.0', 'text'),
        'port': ConfigElement(80, 'integer'),
    },
    'relay 1': {
        'name': ConfigElement('Relay 1', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 2': {
        'name': ConfigElement('Relay 2', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 3': {
        'name': ConfigElement('Relay 3', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 4': {
        'name': ConfigElement('Relay 4', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 5': {
        'name': ConfigElement('Relay 5', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 6': {
        'name': ConfigElement('Relay 6', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 7': {
        'name': ConfigElement('Relay 7', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
    'relay 8': {
        'name': ConfigElement('Relay 8', 'text'),
        'pin': ConfigElement('22', 'text'),
    },
}


def save_config():
    global config
    array = {}
    with open('config.json', 'w', encoding='utf-8') as f:
        for group in config:
            array[group] = {}
            for field in config[group]:
                array[group][field] = config[group][field].value
        print("Storing configuration", array)
        json.dump(array, f)
        f.close()

def get_config():
    global config
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            array = json.loads(f.read())
            print("Reading configuration", array)
            for group in array:
                for field in array[group]:
                    config[group][field].value = array[group][field]
            f.close()
    except Exception as e:
        pass
        # save_config()

if __name__ == '__main__':
    class ConfigEncoder(json.JSONEncoder):
        def default(self, obj):
            return obj.value


    json_str = json.dumps(config, cls=ConfigEncoder)
    print("Org:", json_str)

    config['wifi']['key'].value = 'No shit'

    print("Savinf to file")
    save_config()

    print("Reading form file")
    get_config()

    print("Result:")
    json_str = json.dumps(config, cls=ConfigEncoder)
    print(json_str)
