from common import *

class ConfigElement:
        def __init__(self, value=None, type=None, hint=None, advanced=None):
            self.value = value if value else ""
            self.type = type if type else "text"
            self.advanced = advanced if advanced else False
            self.hint = hint if hint else ""


# Default/factory configuration
config = defaults = {
    'wifi': {
        'enable': ConfigElement('on', 'checkbox', "Enable: connect to existing WiFi. Disable to activate accespoint method"),
        'ssid': ConfigElement('', 'text', 'ID for access point/router (0 - 32 characters)'),
        'key': ConfigElement('', 'password', 'Authorisation key to gain access (0 - 63 characters)'),
    },
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

def store():
    global config
    array = {}
    with open('config.json', 'w', encoding='utf-8') as f:
        for group in config:
            array[group] = {}
            for field in config[group]:
                array[group][field] = config[group][field].value
        debug("Storing configuration: {}".format(array))
        json.dump(array, f)
        f.close()


def retrieve():
    global config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            array = json.loads(f.read())
            debug(f"Reading configuration: {array}")
            for group in array:
                for field in array[group]:
                    config[group][field].value = array[group][field]
            f.close()
    except Exception as e:
        debug(f"Failed to read configuration: {e}")
        # save_config()


def delete():
    global config, defaults
    debug("Deleting stored configuration")
    config = defaults
    return os.remove('config.json')