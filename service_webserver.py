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
import ubinascii

try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from config import *


def page_wrapper(page_name, page_content):
    document = '''<!DOCTYPE html>
        <head>
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
    menu = '<nav id="navigation">\n'
    for title in config.keys():
        menu += '<a class ="navigationlink{0}" href="{1}.html" > {2} </a>\n'.format(
            ' activelink' if title.lower() == page_name.lower() else '',
            title.lower(),
            title[:1].upper() + title[1:]
        )
    menu += '</nav>\n'
    return document.format(
        page_name[:1].upper() + page_name[1:].lower(),
        menu,
        page_content
    )


def get_config_as_html_table_row(request, name):
    row = ""
    try:
        enabled = (config['status'][name.lower()].value == 'on')
    except Exception as e:
        enabled = False
        pass

    if enabled:
        row = '<tr><td>'
        try:
            if name == 'access point mode':
                row += 'Access point mode:</td><td>'
                row += 'Yes' if network.WLAN(network.AP_IF).active() else 'No'
            elif name == 'wifi connected':
                row += 'WiFi connected:</td><td>'
                row += 'Yes' if network.WLAN(network.STA_IF).active() else 'No'
            elif name == 'network':
                row += 'Network setup: ' + network.WLAN(network.STA_IF).ifconfig()
            elif name == 'client':
                row += 'Client connected:</td><td>'
                print(vars(request))
                row += request.UserAddress[0]
            elif name == 'web access':
                row += 'Web access:</td><td>Enabled'
            elif name == 'disk space':
                row = '</td></tr></table><table><tr><td>'
                row += 'Disk space:</td><td>'
                s = os.statvfs('./')
                row += str((s[0] * s[2]) // 1048576) + ' MB'
            elif name == 'disk space free':
                row += 'Disk space free:</td><td>'
                s = os.statvfs('./')
                row += str((s[0] * s[3]) // 1048576) + ' MB'
            elif name == \
                    'cpu':
                pass

        except Exception as e:
            row += 'Not available ({})'.format(e)
        row += '</td></tr>\n'

    return row


def status_page(request):
    box = '''
        <table>
        {}
        </table>
        '''
    return box.format(
        ''.join(
            get_config_as_html_table_row(request, name) + '\n' for name in config['status'].keys()
        )
    )


# Use pyhtml ?
def dyn_page_handler(request, response):
    name = request.path.rsplit('.', 1)[0].lower().rsplit('/', 1)[1]
    page_name = name if name in config.keys() else 'status'
    print(" Dynamic page request from client: ", page_name)
    if page_name == 'status':
        content = status_page(request)
    else:  # Configurations pages
        content = '<table>'
        for lable in config[page_name].keys():
            content += '<tr><td><lable>{0}</lable></td><td><input type="{1}" name="{2}" value="{3}"></td></tr>\n'.format(
                lable[:1].upper() + lable[1:].lower(),
                config[page_name][lable].type,
                lable.lower(),
                config[page_name][lable].value
            )
        content += '</table>'
    html = page_wrapper(page_name, content)
    yield from picoweb.start_response(response)
    yield from response.awrite(html)


def api_handler(request, request_page):
    print('API request from client:', request.UserAddress)
    name = request.path.rsplit('.', 1)[0].lower().rsplit('/', 1)[1]
    print("Q:", request._method, name)
    print(request.GetPostedURLEncodedForm())
    response = '{"id":"1"}'
    request.Response.ReturnOk(response)


def get_mimetype(file_name):
    extensions = ('gif','png','jpg','ico','css','json')
    mimetypes = ('image/gif', 'image/png', 'image/jpg', 'image/x-icon', 'text/css', 'application/json')
    try:
        i = extensions.index(file_name.rsplit('.', 1)[1].lower())
        return mimetypes[i]
    except Exception as e:
        return 'text/html; charset=utf-8'


def file_handler(request, response):
    file_name = config['webserver']['document root'].value + request.path
    print("Request file: ", file_name)
    yield from app.sendfile(response, file_name, content_type=get_mimetype(file_name))

app = None
def start():
    global app
    routes = [
        ("/", dyn_page_handler),
        ("/index.html", dyn_page_handler),
        ("/theme.css", file_handler),
        ("/favicon.ico", file_handler),
        ("/logo.png", file_handler),
        ("/logo.gif", file_handler),
        ("/test.pyhtml", file_handler),
        # (re.compile("^/iam/(.+)"), hello),
    ]
    for label in config.keys():
        routes.append(("/" + label + ".html", dyn_page_handler))

    app = picoweb.WebApp(None, routes)
    app.init()
    app.debug = int(True)
    app.log = None
    if app.debug >= 0:
        import ulogging
        app.log = ulogging.getLogger("picoweb")
        app.log.setLevel(ulogging.DEBUG)
    task = asyncio.start_server(app._handle, host=config['webserver']['host ip'].value, port=config['webserver']['port'].value)
    print("+---------------------------------------------+")
    print(" Webserver running at http://%s:%d " % (config['webserver']['host ip'].value, config['webserver']['port'].value))
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
            print("Already connected")
            print(station.ifconfig())
            return

        station.active(True)
        station.connect(ssid, password)

        while station.isconnected() == False:
            pass

        print("Connection successful")
        print(station.ifconfig())


    async def start_services():
        gc.collect()
        tasks = [
            asyncio.create_task(start()),
        ]
        await asyncio.gather(*tasks)
        print("All tasks have completed now.")


    connect()
    asyncio.run(start_services())
