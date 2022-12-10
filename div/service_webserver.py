# ESP32 service webserver
# using picoweb
# serving static files from /www and handling dynamic pages
#
# picoweb dependencies:
# import upip
# upip.install('micropython-uasyncio')
# upip.install('micropython-pkg_resources')

# captive portal:
# https://github.com/anson-vandoren/esp8266-captive-portal
# https://lemariva.com/blog/2019/01/white-hacking-wemos-captive-portal-using-micropython


import picoweb
import network
import os
try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio

from common import *
from config import config


def mimetype(file_name):
    extensions = ('gif', 'png', 'jpg', 'ico', 'css', 'json')
    mimetypes = ('image/gif', 'image/png', 'image/jpg', 'image/x-icon', 'text/css', 'application/json')
    try:
        i = extensions.index(file_name.rsplit('.', 1)[1].lower())
        return mimetypes[i]
    except Exception as e:
        return 'text/html; charset=utf-8'


# Static file handler - needed expand to handle gif, ico and css files
def static_file_handler(request, response):
    file_name = config['webserver']['document_root'].value + request.path
    debug("Request file: {}".format(file_name))
    header = {'Cache-Control': 'public, max - age = 15552000'}
    yield from service.webserver.sendfile(response, file_name, content_type=mimetype(file_name), headers=header)
    return True


def start(host=None, port=None, routes=None):
    global service

    service.webserver = picoweb.WebApp(None, routes)
    service.webserver.init()
    service.webserver.debug = int(True)
    service.webserver.log = None
    if service.webserver.debug >= 0:
        import ulogging
        service.webserver.log = ulogging.getLogger("picoweb")
        service.webserver.log.setLevel(ulogging.DEBUG)

    task = asyncio.start_server(service.webserver._handle, host=host, port=port)
    print("+---------------------------------------------+")
    print(" Webserver running at http://%s:%d " % (host, port))
    print("+---------------------------------------------+")
    return task


# Dynamic pages

menu_item = (
    'dashboard',
    'status',
    'setup'
)

html = {
    'begin': '<form method="POST"><input type="text" name="function" value="none" hidden><table>\n',
    'header': '<tr><td><h1>{0}</h1></td></tr>\n',
    'button': '<tr><td colspan="2"><button type="button" onclick="cmd(\'{1}\');">{0}</button></td></tr>\n',
    'slider': '<tr><td><label>{0}</label></td><td><label class="slider_l">\n'
                     '<input type="checkbox" {2} onclick="cmd(\'{1} \' + this.checked);this.checked!=this.checked">\n'
                     '<span class="slider round"></span></label></td></tr>\n',
    'checkbox': '<tr><td><label>{0}</label></td><td><input type="checkbox" name="{1}" {2}"></td></tr>\n',
    'text': '<tr><td><label>{0}</label></td><td><input type="text" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    'password': '<tr><td><label>{0}</label></td><td><input type="password" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    'end': '</table></form>\n'
}


def send_page(request, response, page_content):
    document = '''<!DOCTYPE html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1"> 
        <meta charset="UTF-8">
        <link rel="stylesheet" href="/theme.css" type="text/css">
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <title>{0}</title>
        <script>
        function cmd(cmd){{
            var ajax = new XMLHttpRequest();
            ajax.open("POST", "api", true);
            ajax.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            ajax.send('cmd=' + cmd);
        }} 
        </script>
        </head>
        <body>
        <div id="all">
        <header id="header">
        <span class="logo"><img src="logo.gif" width="90px" height="90px"/></span>
        <h1 id="heading">{0}</h1>
        {1}
        </header>
        <main id="main">
        {2}
        </main>
        <footer id="footer">
        Pirates foot
        </footer>
        </div>
        </body>
        </html>
        '''

    menu = '<nav class="navigation">\n'
    add_item = '<a class ="navigationlink{0}" href="{1}.html" > {2} </a>\n'
    for title in menu_item:
        current_page = title.lower() == request.page_name.lower()
        menu += add_item.format(
            ' activelink' if current_page else '',
            title.lower(),
            title[:1].upper() + title[1:]
        )
    menu += '</nav>\n'

    html = document.format(
        request.page_name[:1].upper() + request.page_name[1:].lower(),
        menu,
        page_content
    )
    yield from picoweb.start_response(response)
    yield from response.awrite(html)


def pre_process_request(request):
    name = request.path.rsplit('.', 1)[0].lower().rsplit('/', 1)[1]
    page_name = name if name in menu_item else menu_item[0]
    debug(" Dynamic page request from client: ", page_name, request.method)
    request.page_name = page_name

def dashboard_page(request, response):
    pre_process_request(request)
    content = html['begin']
    for i in range(0, service.relay.relays):
        content += html['slider'].format(service.relay.name(i), f"relay {i}", '')
    content += html['end']
    yield from send_page(request, response, content)
    return True


def setup_page(request, response):
    global config
    debug(f"Setup page {request.method}", DEBUG)
    pre_process_request(request)
    content = html['begin']
    for label in sorted(config.keys()):
        header_done = False
        for field in sorted(config[label].keys()):
            if config[label][field].advanced: continue
            if not header_done:
                content += html['header'].format(label)
                header_done = True
            if config[label][field].type == 'text':
                content += html['text'].format(field, 'config/%s %s' % (label, field), config[label][field].value)
            if config[label][field].type == 'password':
                content += html['password'].format(field, 'config/%s %s' % (label, field), config[label][field].value)
            elif config[label][field].type == 'checkbox':
                content += html['slider'].format(field, 'config/%s %s' % (label, field), 'checked' if config[label][field].value == 'on' else '')
            elif config[label][field].type == 'slider':
                content += html['slider'].format(field, '%s-%s' % (label, field), 'checked' if config[label][field].value == 'on' else '')
    content += html['button'].format('Save configuration', 'config data save')
    content += html['button'].format('Factory reset', 'config data reset')
    content += html['end']

    yield from send_page(request, response, content)
    return True


def status_page(request, response):
    def add_row(label, status):
        return '<tr><td>{0}</td><td>{1}</td></tr>\n'.format(label, status)

    def add_header(label):
        return '<tr><td colspan="2"><h1>{0}</h1></td></tr>\n'.format(label)

    pre_process_request(request)
    content = '<table>\n'
    content += add_header('Network')
    content += add_row('Access point mode', 'Yes' if network.WLAN(network.AP_IF).active() else 'No')
    content += add_row('Connected to WiFi', 'Yes' if network.WLAN(network.STA_IF).active() else 'No')
    cfg = network.WLAN(network.STA_IF).ifconfig()
    try:
        content += add_row('Network interface settings', f'{cfg[0]}</br>{cfg[1]}</br>{cfg[2]}</br>{cfg[3]}')
    except Exception:
        pass
    """

            elif name == 'web access':
                row += 'Web access:</td><td>Enabled''
    """
    content += add_header('File system')
    s = os.statvfs('./')
    content += add_row('Disk space', str((s[0] * s[2]) // 1024) + ' KB')
    content += add_row('Disk space free', str((s[0] * s[3]) // 1024) + ' KB')
    content += '</table>\n'
    yield from send_page(request, response, content)
    return True


# Use pyhtml ?
# Nor really implementet yet :)
def api_handler(request, response):
    global service
    pre_process_request(request)
    debug(f'API request :{request.path}')
    if request.method == "POST":
        yield from request.read_form_data()
        debug(f"Request POST data: {request.form}")
        if 'cmd' in request.form:
            reply = service.cmd(request.form['cmd'])
    yield from send_page(request, response, reply)
    return True



if __name__ == '__main__':
    import gc


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
            'ssid': ConfigElement('', 'text'),
            'key': ConfigElement('', 'password')
        },
        'setup': {
            'webserver setup enable': ConfigElement('on', 'checkbox'),
            'password': ConfigElement('', 'password'),
        }
    }


    def connect():
        ssid = "No connection"
        ssid = "Network_not_found"
        password = "sommerhat."

        station = network.WLAN(network.STA_IF)

        if station.isconnected() == True:
            debug("Already connected", INFO)
            print(station.ifconfig())
            return

        station.active(True)
        station.connect(ssid, password)

        while station.isconnected() == False:
            pass

        debug("Connection successful", INFO)
        print(station.ifconfig())


    async def start_services(host=None, port=None, routes=None):
        gc.collect()
        tasks = [
            asyncio.create_task(start(host=None, port=None, routes=None)),
        ]
        await asyncio.gather(*tasks)
        debug("All tasks has completed or ended with errors", ERROR)


    connect()
    asyncio.run(start_services())
