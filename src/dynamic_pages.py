# Dynamic page handlers
try:
    import network
    import usocket as socket
    import uasyncio as asyncio
    platform = 'ESP'

except:
    import socket
    import asyncio
    import psutil
    platform = 'PC'

import gc
import os
import json
from common import *


HEADER_OK = 'HTTP/1.x 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
HEADER_NOT_FOUND = 'HTTP/1.x 404 Not Found\r\n\r\n'

# format title, navigation menu
HTML_DOCUMENT_BEGIN = '''<!DOCTYPE html>
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
    '''
HTML_DOCUMENT_END = '''
    </main>
    <footer id="footer">
    Pirates foot
    </footer>
    </div>
    </body>
    </html>
    '''

HTML = {
    'begin': '<form method="POST"><input type="text" name="function" value="none" hidden><table>\n',
    'header': '<tr><td><h1>{0}</h1></td></tr>\n',
    'navigation': '<nav class="navigation">\n{0}</nav>\n',
    'nav_item': '<a class ="navigationlink{0}" href="/{1}"> {2} </a>\n',
    'button': '<tr><td colspan="2"><button type="button" onclick="cmd(\'{1}\');">{0}</button></td></tr>\n',
    'slider': '<tr><td><label>{0}</label></td><td><label class="slider_l">\n'
              '<input type="checkbox" {2} onclick="cmd(\'{1} \' + this.checked);this.checked!=this.checked">\n'
              '<span class="slider round"></span></label></td></tr>\n',
    'checkbox': '<tr><td><label>{0}</label></td><td><input type="checkbox" name="{1}" {2}"></td></tr>\n',
    'text': '<tr><td><label>{0}</label></td><td>'
            '<input type="text" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    'password': '<tr><td><label>{0}</label></td><td>'
                '<input type="password" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    'end': '</table></form>\n'
}

menu_item = (
    'dashboard',
    'status',
    'setup'
)


async def page_handler(request, writer):
    route = request.path()[1:].lower()
    if route.startswith('api'):
        await api_handler(request, writer)
        return

    route = route if route in menu_item else menu_item[0]
    writer.write(HEADER_OK.encode('ascii'))
    unical_route = route[:1].upper() + route[1:]
    menu = ''
    for title in menu_item:
        menu += HTML['nav_item'].format('_active' if route == title else '', title, title[:1].upper() + title[1:])
    writer.write(HTML_DOCUMENT_BEGIN.format(unical_route, HTML['navigation'].format(menu)).encode('utf8'))

    if route == 'dashboard':  await dashboard_page(request, writer)
    if route == 'status':      await status_page(request, writer)
    if route == 'setup':      await setup_page(request, writer)

    writer.write(HTML['end'].encode('utf8'))


async def dashboard_page(request, writer):
    writer.write(b'<table>\n')
    reply = cmd('relay all')
    if reply and reply[0] == 'ok':
        for line in reply[1:]:
            if(len(line)):
                relay = line.rpartition(' ')
                writer.write(HTML['slider'].format(relay[0], f"relay {relay[0]}", relay[2]).encode('utf8'))
    else:
        writer.write("No relays configured")
    writer.write(b'</table>\n')


# TODO: restart after facrtory reset
async def setup_page(request, writer):
    global config
    writer.write(b'<table>\n')
    for label in config.keys():
        header_done = False
        for field in config[label].keys():
            if config[label][field].advanced: continue
            if not header_done:
                writer.write(HTML['header'].format(label).encode('utf8'))
                header_done = True
            if config[label][field].type == 'text':
                writer.write(
                    HTML['text'].format(field, f"config {label}/{field}", config[label][field].value).encode(
                        'utf8'))
            if config[label][field].type == 'password':
                writer.write(
                    HTML['password'].format(field, f"config {label}/{field}", config[label][field].value).encode(
                        'utf8'))
            elif config[label][field].type == 'checkbox':
                writer.write(HTML['slider'].format(field, f"config {label}/{field}",
                                                   'checked' if config[label][field].value == 'on' else '').encode(
                    'utf8'))
            elif config[label][field].type == 'slider':
                writer.write(HTML['slider'].format(f"config {label}/{field}",
                                                   'checked' if config[label][field].value == 'on' else '').encode(
                    'utf8'))
    writer.write(HTML['button'].format('Save configuration', 'config save').encode('utf8'))
    writer.write(HTML['button'].format('Factory reset', 'config factory_reset').encode('utf8'))
    writer.write(b'</table>\n')


async def status_page(request, writer):
    def add_row(label, status):
        return '<tr><td>{0}</td><td>{1}</td></tr>\n'.format(label, status)

    def add_header(label):
        return '<tr><td colspan="2"><h1>{0}</h1></td></tr>\n'.format(label)

    content = '<table>\n'
    try:
        content += add_header('Network')
        content += add_row('Access point mode', 'Yes' if network.WLAN(network.AP_IF).active() else 'No')
        content += add_row('Connected to WiFi', 'Yes' if network.WLAN(network.STA_IF).active() else 'No')
        cfg = network.WLAN(network.STA_IF).ifconfig()
        content += add_row('Network interface settings', f'{cfg[0]}</br>{cfg[1]}</br>{cfg[2]}</br>{cfg[3]}')
    except Exception:
        pass

    content += add_header('RAM')
    if platform == 'PC':
        memory = psutil.virtual_memory()._asdict()
        free = memory['free']
        allocated = memory['used']
        total = memory['total']
        percent = memory['percent']
    else:
        free = gc.mem_free()
        allocated = gc.mem_alloc()
        total = allocated + free
        percent = round(free / total * 100)

    content += add_row('Allocated ', f"{allocated // 1024} KB {percent}%")
    content += add_row('Free ', f"{free // 1024} KB")
    content += add_row('Toal ', f"{total // 1024} KB")

    content += add_header('File system')
    s = os.statvfs('./')
    content += add_row('Disk space', str((s[0] * s[2]) // 1024) + ' KB')
    content += add_row('Disk space free', str((s[0] * s[3]) // 1024) + ' KB')
    content += '</table>\n'
    writer.write(content.encode('utf8'))


async def api_handler(request, writer):
    global service
    debug(f'API request :{request.path()}')
    reply = 'Failed'
    if request.method() == "POST":
        if 'cmd' in request.body():
            reply = app.cmd(request.body()['cmd'])
    debug(f"Reply: {reply}", DEBUG)
    writer.write(json.dumps(reply).encode('utf8'))

