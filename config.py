import json


class ConfigElement:
        def __init__(self, value=None, type=None):
            self.value = value if value else ""
            self.type = type if type else "text"


config = {
    'status': {
        'access point mode': ConfigElement('on', 'checkbox'),
        'wifi connected': ConfigElement('on', 'checkbox'),
        'network': ConfigElement('on', 'checkbox'),
        'client': ConfigElement('on', 'checkbox'),
        'web access': ConfigElement('on', 'checkbox'),
        'disk space': ConfigElement('on', 'checkbox'),
        'disk space free': ConfigElement('on', 'checkbox'),
        'ram': ConfigElement('on', 'checkbox'),
        'ram free': ConfigElement('on', 'checkbox'),
        'cpu': ConfigElement('on', 'checkbox')
    },
    'wifi': {
        'enable': ConfigElement('on', 'checkbox'),
        'ssid': ConfigElement('<SSID>', 'text'),
        'key': ConfigElement('<KEY>', 'password')
    },
    'setup': {
        'webserver setup enable': ConfigElement('on', 'checkbox'),
        'password': ConfigElement('', 'password'),
    },
    'webserver': {
        'document root': ConfigElement('/www', 'text'),
        'host ip': ConfigElement('0.0.0.0', 'text'),
        'port': ConfigElement(80, 'integer'),
    },
}
def save_config():
    global config
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f)
        f.close()

def get_config():
    global config
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            f.close()
    except Exception as e:
        save_config()

