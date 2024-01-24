# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license
# Dynamic page handlers
from common import *

if platform == ESP:
    import network
    import usocket as socket
    import uasyncio as asyncio
else:
    import socket
    import asyncio
    import psutil


import gc
import os
import math

import uwebserver

HEADER_OK = 'HTTP/1.x 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
HEADER_NOT_FOUND = 'HTTP/1.x 404 Not Found\r\n\r\n'
HTML = {
    # First part of HTML header
    'heading part 1': '''<!DOCTYPE html>
        <head>
        <meta content="width=device-width, initial-scale=1" name="viewport">
        <meta charset="UTF-8">
        <link href="theme.css" rel="stylesheet" type="text/css">
        <link href="/favicon.ico" rel="icon" type="image/x-icon">
        <script src="helpers.js"></script>
        <title>''',
    # insert title here

    # page header
    'heading part 2': '''
        </title>
        </head>
        <body>
        <header id="header">
          <span class="logo"><img class="logo" src="logo.gif"/></span>
          <h1 id="heading">{0}</h1>
          <div class="header-right">
            <label>Adv. view</label>
            <label class="slider_l">
              <input class="free-slider-input" onclick="advanced_toggle_view(this.checked)" type="checkbox">
              <span class="slider round"></span></label>
          </div>
          <nav class="navigation">''',

    # insert navigation items {0} = checked | <empty> {1} = href  {2} link text with unical
    'nav_item': '<a class ="navigationlink{0}" href="{1}"> {2} </a>\n',

    # End page heading
    'heading part 3': '''
    </nav>
    </header>
    ''',

    # First part of main container
    'main part 1': '''
    <div class="main">
      <div class="tabs">
        <table class="tab">
          <tr>''',
    # insert a number of tab items {0} = Title
    'tab_item': '''
    <td>
      <input id="{0}" {1} name="tab-group-1" onclick="tab_select(this.id+'-cont')" type="radio">
      <label for="{0}">{0}</label>
    </td>
    ''',
    # End of tabs
    'main part 2': "</tr></table>\n",

    # Insert corresponding number of tab contents (or terminal)
    'tab_content_begin': '<table class="content" id="{0}-cont">'+"\n",

    # Terminal
    'tab_content_terminal': '''<div class="console content" id="{0}-cont" onclick="consoleFocus()">
        <div id="console-output">
          Ready.<br>
        </div>
        <div class="console-input">
        <span>></span>
        <textarea id="console-input" type="text" onkeydown = "consoleInput();" rows=10 cols = 38></textarea>
        </div>
        <script type="text/javascript">consoleStart("{0}-cont")</script>''',

    # Insert Headline {0} = text
    'tab_content_heading': '<tr {1}><td colspan="2"><h1>{0}</h1></td></tr>'+"\n",

    # Insert text {0}=label, {1}=value, {2}=advanced
    'tab_content_text': '''
        <tr {2}><td><label>{0}</label></td>
        <td>{1}</td></tr>'''+"\n",

    # Insert input {0} = label, {1} = command <value>, {2} = value, {3}=hint, {4}= advanced
    'tab_content_input': '''
        <tr {4} title="{3}"><td><label>{0}</label></td>
        <td><input onblur="cmd('{1} ' + this.value)" type="text" value="{2}"></td></tr>'''+"\n",

    # Insert Slider {0}=label, {1}=command <value of checked>, {2}=checked | <empty>, {3}=hint, {4}=advanced view class
    'tab_content_slider': '''
    <tr title="{3}" {4}><td><label>{0}</label></td><td><label class="slider_l">
    <input type="checkbox" {2} onclick="cmd('{1} ' + this.checked);">
    <span class="slider round"></span></label></td></tr>'''+"\n",

    # Insert button {0}=label, {1}=command , {2}=hint, {3}=advanced view class
    'tab_content_button': '''<tr title="{2}" onclick="cmd(\'{1} \');" class="button_label glow-on-hover {3}">
    <td>{0}</td>
    <td><span class="button"></span></td>
    </tr>'''+"\n",

    # Insert input {0} = label, {1} = percentage <value>, {2}=hint, {3}= advanced
    'tab_content_meter': '''<tr title="{2}" {3}>
        <td>{0}</td> 
        <td><meter low="70" high="90" min="0" max="100" optimum="0" value="{1}"></meter> {1}%</td>
        <tr>
    ''',

    # Insert selector {0}=label, {1}=command, [2}= hint, {3}=advanced view class
    'tab_content_select_begin': '<tr title="{2}" {3}><td><label>{0}</label></td><td><select name="{0}" onchange="cmd(\'{1}\' + this.value)">'+"\n",
    'tab_content_select_end': '</select></td></tr>'+"\n",
    # Insert selector_option {0}=option, {1}==selected
    'tab_content_select_option': '<option value="{0}" {1}>{0}</option>'+"\n",

    # End tab content
    'tab_content_end': "</table>\n",

    # End of page
    'main part 3': '''
    </div>
    <div id="notification" class="notification"></div>
    <footer>
    <a href="github.com/paragi/enp-1">ENP-1</a>
    </footer>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function(){
            tab_select("{0}-cont");           // Select first tab
            advanced_toggle_view(false); // Disable advanced view
        }, false);
    </script>
    </body>''',

    # 'script': "<script type=\"text/javascript\">{0}</script>\n",

    # 'checkbox': '<tr><td><label>{0}</label></td><td><input type="checkbox" name="{1}" {2}"></td></tr>\n',
    # 'password': '<tr><td><label>{0}</label></td><td>'
    #           '<input type="password" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    # 'end': '</table></form>\n'
    # 'begin': '<form method="POST"><input type="text" name="function" value="none" hidden><table>\n',
    # 'header': '<tr><td><h1>{0}</h1></td></tr>\n',
    # 'navigation': '<nav class="navigation">\n{0}</nav>\n',
    # 'text': '<tr><td><label>{0}</label></td><td>'
    #        '<input type="text" value="{2}" onblur="cmd(\'{1} \' + this.value)"></td></tr>\n',
    # 'tabs': '  <div class="tabs">{0}</div>',
    # 'tab': '<div class="tab"><input type="radio" name="css-tabs" id="{0}" checked class="tab-switch">'
    #    '<label for="{0}" class="tab-label">Tab One</label>'
    #    '<div class="tab-content">{1}</div>'
    #    '</div>',
}

# TODO: handle errors in async
# NB: str.format() just hang, if parameters are missing. Be careful to supply all.

class SendHTML():
    def __init__(self, writer):
        self.writer = writer
        self.active_tab = ''

    def page_heading(self, title: str, page: str, pages: tuple):
        # HTML and page layout header
        self.writer.write(HTML['heading part 1'].encode('utf8'))

        CurrentUnicalPageName = page[:1].upper() + page[1:]

        # Title
        unicalTitle = title[:1].upper() + title[1:]
        self.writer.write(unicalTitle.encode('utf8'))

        # Page navigation
        self.writer.write(HTML['heading part 2'].format(unicalTitle).encode('utf8'))
        for pageName in pages:
            unicalPageName = pageName[:1].upper() + pageName[1:]
            state = '_active' if CurrentUnicalPageName == unicalPageName else ''
            self.writer.write(HTML['nav_item'].format(state, pageName, unicalPageName).encode('utf8'))

        self.writer.write(HTML['heading part 3'].encode('utf8'))

    def tab_titles(self, tabs: tuple):
        self.writer.write(HTML['main part 1'].encode('utf8'))
        firstTab = tabs[0]
        for tab in tabs:
            checked = 'checked' if tab == firstTab else ''
            self.writer.write(HTML['tab_item'].format(tab, checked).encode('utf8'))
        self.writer.write(HTML['main part 2'].encode('utf8'))
        self.active_tab = tabs[0]

    def tab_content_terminal(self, title: str):
        self.writer.write(HTML['tab_content_terminal'].replace('{0}',title).encode('utf8'))

    def tab_content_begin(self, title: str):
        self.writer.write(HTML['tab_content_begin'].format(title).encode('utf8'))

    def tab_content_heading(self, text: str, advanced: bool = False):
        advancedView = 'class="advanced"' if advanced else ''
        self.writer.write(HTML['tab_content_heading'].format(text, advancedView).encode('utf8'))

    def tab_content_text(self,label: str, text: str, advanced: bool = False):
        advancedView = 'class="advanced"' if advanced else ''
        self.writer.write(HTML['tab_content_text'].format(label, text, advancedView).encode('utf8'))

    def tab_content_input(self, label: str, command: str, value: str, hint: str = '', advanced: bool = False):
        advancedView = 'class="advanced"' if advanced else ''
        self.writer.write(HTML['tab_content_input'].format(label, command, value, hint, advancedView).encode('utf8'))

    def tab_content_slider(self, label, state, command, hint, advanced: bool = False):
        state = 'checked' if state else ''
        advancedView = 'class="advanced"' if advanced else ''
        self.writer.write(HTML['tab_content_slider'].format(label, command, state, hint, advancedView).encode('utf8'))

    def tab_content_button(self, label: str, command: str, hint: str = '', advanced: bool = False):
        advancedView = 'advanced' if advanced else ''
        self.writer.write(HTML['tab_content_button'].format(label, command, hint, advancedView).encode('utf8'))

    def tab_content_selector(self, label, options, value, command, hint: str = '', advanced: bool = False):
        advancedView = 'class="advanced"' if advanced else ''
        self.writer.write(HTML['tab_content_select_begin'].format(label, command, hint, advancedView).encode('utf8'))
        for option in options:
            selected = 'selected' if value == option else ''
            self.writer.write(HTML['tab_content_select_option'].format(option, selected).encode('utf8'))
        self.writer.write(HTML['tab_content_select_end'].encode('utf8'))

    def tab_content_meter(self, label, percentage, hint: str = '', advanced: bool = False):
        if isinstance(percentage, str):
            self.tab_content_text(label, percentage, advanced)
        else:
            advancedView = 'class="advanced"' if advanced else ''
            self.writer.write(HTML['tab_content_meter'].format(label, percentage, hint, advancedView).encode('utf8'))

     # Create content from a dictionary of presentation data objects or similar.
    def tab_content_from_dict(self, tab, array:dict):
        for label in array:
            action = ''
            if hasattr(array[label], 'action'):
                action = array[label].action
            if isinstance(array[label].type,  (list, tuple)):
                self.tab_content_selector(label, array[label].type, array[label].value, array[label].hint, array[label].advanced)
            if array[label].type == 'heading':
                self.tab_content_heading(array[label].value, array[label].advanced)
            elif array[label].type in('text','int','float','password'):
                self.tab_content_text(label, array[label].value, array[label].advanced)
            elif array[label].type == 'input':
                self.tab_content_input(label, action, array[label].value, array[label].hint, array[label].advanced)
            elif array[label].type == 'slider':
                self.tab_content_slider(label, array[label].value, action, array[label].hint, array[label].advanced)
            elif array[label].type == 'button':
                self.tab_content_button(label, action, array[label].hint, array[label].advanced)
            else:
                debug(f"unable to present type:'{array[label].type}' from presentation data by {tab}/{label}",ERROR,DEBUG)

    def tab_content_end(self):
        self.writer.write(HTML['tab_content_end'].encode('utf8'))

    def page_end(self):
        self.writer.write(HTML['main part 3'].replace('{0}', self.active_tab).encode('utf8'))

menu_item = (
    'dash',
    'status',
    'setup',
    'tools'
)

async def page_handler(request, writer):
    try:
        # Get route in lower case without initial slash
        route = request.path().lower().replace('/','')
        writer.write(HEADER_OK.encode('ascii'))

        # Catch api call
        if route.startswith('api'):
            debug(f'API request :{request.path()}', DEBUG)
            reply = 'failed (1) \nAccepts only http POST requests'
            if request.method() == "POST":
                reply = app.cmd(request.body())
            writer.write(reply.encode('utf8'))
            debug(f"API Reply: {reply}", DEBUG)
            return

        # Generate dynamic page from template. Default route to first menu element
        sendHTML = SendHTML(writer)
        route = route if route in menu_item else menu_item[0]
        sendHTML.page_heading(config['general']['devicename'].value, route,  menu_item)
        # Populate page content
        if route == 'dash':   await dashboard_page(request, sendHTML)
        if route == 'status': await status_page(request, sendHTML)
        if route == 'setup':  await setup_page(request, sendHTML)
        if route == 'tools':  await tool_page(request, sendHTML)

        sendHTML.page_end()
    except Exception as e:
        debug(e)


async def dashboard_page(request, sendHTML):
    tabs = []
    for groupName in app.dashboard:
        tabs.append(groupName)

    if not len(tabs):
        return

    sendHTML.tab_titles(tabs)

    for groupName in app.dashboard:
        try:
            sendHTML.tab_content_begin(groupName)
            if callable(app.dashboard[groupName]):
                sendHTML.tab_content_from_dict(groupName, app.dashboard[groupName]())
            sendHTML.tab_content_end()
        except Exception as e:
            debug(e)


# TODO: restart after facrtory reset
async def setup_page(request, sendHTML):
    tabs = [key[:1].upper() + key[1:] for key in config]
    sendHTML.tab_titles(tabs)

    for group in config:
        tabName = group[:1].upper() + group[1:]
        sendHTML.tab_content_begin(tabName)

        for label in config[group]:
            if isinstance(config[group][label].type,  (list, tuple)):
                sendHTML.tab_content_selector(
                    label,
                    config[group][label].type,
                    config[group][label].value,
                    f"config {group}/{label} ",
                    config[group][label].hint,
                    config[group][label].advanced
                )
            elif isinstance(config[group][label].type,  str):
                if config[group][label].type in ('text', 'int', 'password'):
                    sendHTML.tab_content_input(
                        label,
                        f"cfg {group}/{label}",
                        config[group][label].value,
                        config[group][label].hint,
                        config[group][label].advanced
                    )
                elif config[group][label].type == 'bool':
                    sendHTML.tab_content_slider(
                        label,
                        config[group][label].value,
                        f"cfg {group}/{label}",
                        config[group][label].hint,
                        config[group][label].advanced
                    )
        sendHTML.tab_content_button('Save', 'cfg save', "Save cfguration permanently", False)
        sendHTML.tab_content_button('Resart', 'restart', "Restart device, for new setting to take effect", False)

        sendHTML.tab_content_end()

def roundMemSize(x):
    i = 0
    suffixes = ('Bytes', 'kB', 'MB', 'GB', 'TB')
    while x > 1024:
        i += 1
        x = x / 1024
    return f"{math.ceil(x)} {suffixes[i]}"

def sendContent(sendHTML, title, info):
    sendHTML.tab_content_begin(title)
    for label in info:
        if info[label] == 'heading':
            sendHTML.tab_content_heading(label)
        elif isinstance(info[label], int):
            sendHTML.tab_content_meter(label, info[label])
        elif len(info[label]):
            sendHTML.tab_content_text(label, info[label])
        else:
            sendHTML.tab_content_text(label, 'Unknown')
    sendHTML.tab_content_end()


async def status_page(request, sendHTML):
    tabs = ['Resources','Network','Time']
    sendHTML.tab_titles(tabs)
    # Resources
    info = {}
    info['CPU'] = 'heading'
    try:
        if platform == PC: # Unix
            info['CPU utilization'] = int(psutil.cpu_percent())
            info['Memory'] = 'heading'
            memory = psutil.virtual_memory()._asdict()
            info['RAM Total'] = roundMemSize(memory['total'])
            info['RAM Used'] = str2int(memory['percent'])
        else:
            info['CPU utilization'] = 'Unknown'
            info['Memory'] = 'heading'
            free = gc.mem_free()
            allocated = gc.mem_alloc()
            info['RAM Total'] = roundMemSize(allocated + free)
            info['RAM Used'] = str(round(free * 100 / (allocated + free)))
    except Exception as e:
        info['CPU utilization'] = 'Unknown'
        info['RAM Total'] = 'Unknown'
        info['RAM Used'] = 'Unknown'

    info['File system'] = 'heading'
    s = os.statvfs('./')
    info['Total disk space'] = roundMemSize(s[0] * s[2])
    info['Disk used'] = round((s[2] - s[4]) * 100 / s[2])
    sendContent(sendHTML, tabs[0], info)

    # Network
    info = {}
    info['AP/Client mode'] = config['wifi']['mode'].value
    info['As Wifi client'] = 'heading'
    info['SSID'] = config['wifi']['ssid'].value
    info['Key'] = config['wifi']['key'].value

    try:
        if platform == ESP:
            ip = app.wifi.nic.ifcfg()
            info['IP'] = ip[0]
            info['Subnet mask'] = ip[1]
            info['Gateway'] = ip[2]
            info['DNS'] = ip[3]
            info['Access point'] = 'heading'
            aip = app.wifi.niap.ifcfg()
            info['AP IP'] = aip[0]
            info['AP Subnet mask'] = aip[1]
            info['AP Gateway'] = aip[2]
            info['AP DNS'] = aip[3]

        elif platform == PC:
            # This method of obtaining ip address may fail!
            try:
                info['Host name'] = socket.gethostname()
                info['IP'] = socket.gethostbyname(info['Host name'])
                info['Access point'] = 'heading'
                info['AP SSID'] = config['access point']['ssid'].value
                info['AP Key'] = config['access point']['key'].value
                info['AP Channel'] = str(config['access point']['channel'].value)
                info['AP IP'] = config['access point']['ip'].value
            except Exception as e:
                info['IP'] = ''
    except Exception as e:
        debug(e)
    sendContent(sendHTML, tabs[1], info)

    # Time
    info = {}
    import datetime
    now = datetime.datetime.now()
    print(now.year, now.month, now.day, now.hour, now.minute, now.second)
    info['Time'] = f"{now.hour}:{now.minute}"
    info['Date'] = f"{now.year}-{now.month}-{now.day}"
    sendContent(sendHTML, tabs[2], info)

async def tool_page(request, sendHTML):
    tabs = ['Miscellaneous','Terminal']
    sendHTML.tab_titles(tabs)

    # Miscellaneous
    sendHTML.tab_content_begin(tabs[0])
    sendHTML.tab_content_button('Resart', 'restart', "Restart device, for new setting to take effect", False)
    sendHTML.tab_content_button('Factory reset', 'factory_reset', "Restore device to factory settings permanently", False)
    sendHTML.tab_content_end()

    # terminal
    sendHTML.tab_content_terminal(tabs[1])


async def start():
    try:
        if not app.wifi:
            debug(f"Wifi module not loaded before {__file__}. Webservers not started.")
            return

        if app.wifi.mode != app.wifi.MODE_CLIENT:
            debug(f"Starting webserver for access point")
            while not app.wifi.ip['access_point']:
                await asyncio.sleep(0.3)

            webserver = uwebserver.Webserver(
                host=app.wifi.ip['access_point'],
                port=config['webserver']['access point port'].value,
                dyn_handler=page_handler,
                docroot=config['webserver']['document root'].value
            )
            app.task['webserver access point'] = asyncio.create_task(webserver.start())
            print("--------------------------------------------------")
            print(
                f" Web server started for access point at http://{app.wifi.ip['access_point']}:{config['webserver']['access point port'].value}")
            print("--------------------------------------------------")

        if app.wifi.mode != app.wifi.MODE_AP:
            debug(f"Starting webserver (for LAN client)")
            while not app.wifi.ip['client']:
                await asyncio.sleep(0.3)

            port = config['webserver']['client port'].value
            docroot = config['webserver']['document root'].value

            if platform == PC and port < 1024:
                port = 8080
                docroot = '.' + docroot

            webserver = uwebserver.Webserver(
                host=app.wifi.ip['client'],
                port=port,
                dyn_handler=page_handler,
                docroot=docroot
            )

            app.task['webserver'] = asyncio.create_task(webserver.start())

            print("-------------------------------------------------------------")
            print(f" Web server started for WiFi client at http://{app.wifi.ip['client']}:{port}")
            print("-------------------------------------------------------------")
    except Exception as e:
        debug(e)
    # gc.collect()


config.add('webserver', 'client port', 'int', 80, 'Webserver port (Default 80 on ESP, 8080 on PC)', True)
config.add('webserver', 'document root', 'text', '/www', 'Webservers document root (Default to current directory)', True)
config.add('webserver', 'access point port', 'int', 80, 'Webserver port for access point (Default 80 on ESP, 8080 on PC)', True)

startJob('webserver', start)

