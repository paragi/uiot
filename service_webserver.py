# ESP32 service webserver
# using picoweb
# serving static files from /www and handling dynamic pages
#
# picoweb dependencies:
# import upip
# upip.install('micropython-uasyncio')
# upip.install('micropython-pkg_resources')

import picoweb
import network
import os

try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from common import *

menu_item = (
    'dashboard',
    'status',
    'setup'
)

html = {
    'begin': '<form method="POST"><input type="text" name="function" hidden><table>\n',
    'header': '<tr><td><h1>{0}</h1></td></tr>\n',
    'button': '<tr><td colspan="2"><input type="submit" value="{0}" '
              'onclick="document.getElementsByName(\'function\').value = \'{0}\';"></td></tr>\n',
    'slider_action': '<tr><td><label>{0}</label></td><td><label class="slider_l">\n'
                     '<input name="{1}"type="checkbox" {2} onclick="document.forms[0].submit()">'
                     '<span class="slider round"></span></label></td></tr>\n',
    'slider': '<tr><td><label>{0}</label></td><td><label class="slider_l">\n'
              '<input name="{0}"type="checkbox" {1}><span class="slider round"></span></label></td></tr>\n',
    'checkbox': '<tr><td><label>{0}</label></td><td><input type="checkbox" name="{0}" {1}"></td></tr>\n',
    'text': '<tr><td><label>{0}</label></td><td><input type="text" name="{0}" value="{1}"></td></tr>\n',
    'password': '<tr><td><label>{0}</label></td><td><input type="password" name="{0}" value="{1}"></td></tr>\n',
    'end': '</table></form>\n'
}


def send_page(request, response, page_content):
    document = '''<!DOCTYPE html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/theme.css" type="text/css">
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <title>{0}</title>
        </head>
        <body>
        <div id="all">
        <header id="header">
        <span class="logo"><img src="logo.gif" width="90px" height="90px"/></span>
        <h1 id="heading">{0}</h1>
        {1}
        </header>
        <main id="main">
        <form method="POST">
        <input type="submit" hidden />
        {2}
        </form>        
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


from relay import Relay

relay = Relay(8)


def dashboard_page(request, response):
    pre_process_request(request)
    if request.method == "POST":
        yield from request.read_form_data()
        debug(json.dumps(request.form), DEBUG)
        # TODO: authenticate
        for form_name in request.form:
            debug("processing POST:", form_name, DEBUG)
            if form_name == 'function':
                debug("Function:", str(request.form[form_name]), DEBUG)
                continue
            try:
                # TODO: config relay names
                index = int(str(form_name).split('', 1)[1]) - 1
                relay.set(index, str(request.form[form_name]))
            except Exception as e:
                debug("Form POST error:{}".format(e), ERROR)

    content = html['begin']
    for index in range(0, 8):
        content += html['slider_action'].format(relay.name(index), "R" + str(index), 'checked' if relay.get(index) else '')
    content += html['end']
    yield from send_page(request, response, content)


def setup_page(request, response):
    pre_process_request(request)
    if request.method == "POST":
        yield from request.read_form_data()
        # request.read_form_data()
        debug(json.dumps(request.form), DEBUG)
        # TODO: authenticate
        for form_name in request.form:
            debug("processing POST:{}".format(form_name), DEBUG)
            if form_name == 'function':
                debug("Function:{}".format(request.form[form_name]))
                continue
            try:
                (group, field) = str(form_name).split('-', 1)
                if field in config[group].keys():
                    # TODO: validate
                    config[group][field].value = str(request.form[form_name])
            except Exception as e:
                debug("Form POST error:{}".format(e))
        save_config()

    content = html['begin']
    for label in config.keys():
        content += html['header'].format(label)
        for field in config[label].keys():
            form_name = '%s-%s' % (label, field)
            if config[label][field].type == 'text':
                content += html['text'].format(form_name, config[label][field].value)
            if config[label][field].type == 'password':
                content += html['password'].format(form_name, config[label][field].value)
            elif config[label][field].type == 'checkbox':
                content += html['slider'].format(form_name, 'checked' if config[label][field].value == 'on' else '')
            elif config[label][field].type == 'slider':
                content += html['slider'].format(form_name, 'checked' if config[label][field].value == 'on' else '')
    content += html['button'].format('Save')
    content += html['button'].format('Factory reset')
    content += html['end']

    yield from send_page(request, response, content)


def status_page(request, response):
    pre_process_request(request)
    content = '<table>\n'

    def add_row(label, status):
        return '<tr><td>{0}</td><td>{1}</td></tr>\n'.format(label, status)

    def add_header(label):
        return '<tr><td colspan="2"><h1>{0}</h1></td></tr>\n'.format(label)

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
    file_name = config['webserver']['document root'].value + request.path
    debug("Request file: {}".format(file_name))
    yield from app.sendfile(response, file_name, content_type=mimetype(file_name))


# Use pyhtml ?


# Nor really implementet yet :)
def api_handler(request, response):
    debug('API request from client:{}'.format(request.UserAddress))
    name = request.path.rsplit('.', 1)[0].lower().rsplit('/', 1)[1]
    print("Q:{}".format(request._method, name), DEBUG)
    debug(request.GetPostedURLEncodedForm())
    writer = '{"id":"1"}'
    request.response.ReturnOk(writer)


# Custom start server - Needed to allow multiple tasks to run concurrently.
app = None


def start():
    global app
    routes = [
        ("/", dashboard_page),
        ("/index.html", dashboard_page),
        ("/dashboard.html", dashboard_page),
        ("/setup.html", setup_page),
        ("/status.html", status_page),
        ("/theme.css", static_file_handler),
        ("/favicon.ico", static_file_handler),
        ("/logo.png", static_file_handler),
        ("/logo.gif", static_file_handler),
        ("/test.pyhtml", static_file_handler),
        # (re.compile("^/iam/(.+)"), hello),
    ]

    app = picoweb.WebApp(None, routes)
    app.init()
    app.debug = int(True)
    app.log = None
    if app.debug >= 0:
        import ulogging
        app.log = ulogging.getLogger("picoweb")
        app.log.setLevel(ulogging.DEBUG)
    task = asyncio.start_server(app._handle, host=config['webserver']['host ip'].value,
                                port=config['webserver']['port'].value)
    print("+---------------------------------------------+")
    print(" Webserver running at http://%s:%d " % (
        config['webserver']['host ip'].value, config['webserver']['port'].value))
    print("+---------------------------------------------+")
    return task


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


    async def start_services():
        gc.collect()
        tasks = [
            asyncio.create_task(start()),
        ]
        await asyncio.gather(*tasks)
        debug("All tasks has completed or ended with errors", ERROR)


    connect()
    asyncio.run(start_services())
